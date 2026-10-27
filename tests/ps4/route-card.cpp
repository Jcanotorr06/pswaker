// Real game card manager and SDK locks/threads; external storage and JKR thread
// bookkeeping are simulated. No GCI bytes, disk assets or save durability claim.
#include "m_Do/m_Do_MemCard.h"
#include "m_Do/m_Do_Reset.h"
#include "JSystem/JUtility/JUTGba.h"
#include <cos_sdk/hooks.h>
#include <dolphin/card.h>
#include <dolphin/dvd/dvd.h>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <thread>

extern "C" int pswaker_card_shutdown_status();
// This existing lifecycle harness simulates storage. Whole-save bytes are
// exercised separately through the real GCI/backend application seam.
extern "C" bool pswaker_save_begin(int) { return true; }
extern "C" bool pswaker_save_finish(bool completed) { return completed; }
extern "C" bool pswaker_save_check(int) { return true; }
// Reset context is normally supplied by game startup.
mDoRstData* mDoRst::mResetData = nullptr;
namespace {
std::atomic<unsigned> stores{0};
std::atomic<bool> storageEntered{false}, releaseStorage{false};
bool failStore = false;
bool fileCreated = false;
DVDDiskID disk{};
template<class Predicate> void waitFor(Predicate predicate) {
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(3);
    while (!predicate() && std::chrono::steady_clock::now() < deadline)
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    assert(predicate());
}
}

// The imported game's JKR registration/heap services do not participate in
// this manager protocol. Keep all card/SDK code real and isolate those services.
extern "C" void jkrThreadCtor(void*, OSThread*, int) asm("_ZN9JKRThreadC1EP8OSThreadi");
extern "C" void jkrThreadCtor(void*, OSThread*, int) {}
extern "C" void jkrThreadDtor(void*) asm("_ZN9JKRThreadD1Ev");
extern "C" void jkrThreadDtor(void*) {}
extern "C" void* jkrHeapCurrent(void*) asm("_ZN7JKRHeap17becomeCurrentHeapEv");
extern "C" void* jkrHeapCurrent(void*) { return nullptr; }

s32 mDoMemCdRWm_Store(CARDFileInfo*, void*, u32) {
    ++stores;
    storageEntered = true;
    waitFor([] { return releaseStorage.load(); });
    return failStore ? CARD_RESULT_IOERROR : CARD_RESULT_READY;
}
s32 mDoMemCdRWm_Restore(CARDFileInfo*, void*, u32) { std::abort(); }
extern "C" {
// No clock or SI device is needed to wake an empty GBA queue on shutdown.
OSTime OSGetTime() { return 0; }
u32 SIProbe(s32) { std::abort(); }
void CARDInit(const char*, const char*) {}
DVDDiskID* DVDGetCurrentDiskID() { return &disk; }
s32 CARDMount(s32, void*, CARDCallback) { return CARD_RESULT_READY; }
s32 CARDCheck(s32) { return CARD_RESULT_READY; }
s32 CARDOpen(s32, const char*, CARDFileInfo* info) {
    info->chan = 0; info->fileNo = 0;
    return fileCreated ? CARD_RESULT_READY : CARD_RESULT_NOFILE;
}
s32 CARDCreate(s32, const char*, u32, CARDFileInfo*) {
    fileCreated = true;
    return CARD_RESULT_READY;
}
s32 CARDClose(CARDFileInfo*) { return CARD_RESULT_READY; }
s32 CARDFreeBlocks(s32, s32* bytes, s32* files) {
    *bytes = 1024 * 1024; *files = 100; return CARD_RESULT_READY;
}
BOOL CARDProbe(s32) { return TRUE; }
s32 CARDProbeEx(s32, s32* bytes, s32* sector) {
    *bytes = 1024 * 1024; *sector = 8192; return CARD_RESULT_READY;
}
s32 CARDUnmount(s32) { return CARD_RESULT_READY; }
s32 CARDFormat(s32) { std::abort(); }
}

int main(int argc, char** argv) {
    assert(argc == 2);
    if (!std::strcmp(argv[1], "shutdown-gba")) {
        JUTGba gba;
        std::memset(&gba, 0, sizeof gba);
        JUTGba::sManager = &gba;
        for (int i = 0; i < 4; ++i) {
            auto& param = gba.mParams[i];
            OSInitMessageQueue(&param.msg_q, param.msg, 1);
            assert(OSCreateThread(&gba.mThreads[i], JUTGba::gbaThreadMain, &param,
                                  gba.mStacks+i+1, 0x1000, 8, 0));
            OSResumeThread(&gba.mThreads[i]);
        }
        COSSdkRequestShutdown();
        for (auto& thread : gba.mThreads) assert(OSJoinThread(&thread, nullptr));
        return 0;
    }
    failStore = !std::strcmp(argv[1], "failed-store");
    assert(pswaker_card_shutdown_status() == 1); // Quit before card initialization.
    g_mDoMemCd_control.ThdInit();
    mDoRstData reset{};
    mDoRst::setResetData(&reset);
    g_mDoMemCd_control.update();
    waitFor([] { return g_mDoMemCd_control.getStatus(0) == 1; }); // No save yet.
    assert(pswaker_card_shutdown_status() == 1 && stores == 0);
    char completedRequest[32]{};
    const BOOL interrupts = OSDisableInterrupts();
    g_mDoMemCd_control.save(completedRequest, sizeof completedRequest, 0);
    // The worker cannot take the SDK lock yet: a queued request still blocks Quit.
    assert(pswaker_card_shutdown_status() == 0);
    OSRestoreInterrupts(interrupts);
    waitFor([] { return storageEntered.load(); });
    assert(pswaker_card_shutdown_status() == 0);
    assert(!COSSdkIsShuttingDown()); // Waiting must leave the worker operational.
    releaseStorage = true;
    waitFor([] { return pswaker_card_shutdown_status() != 0; });
    assert(pswaker_card_shutdown_status() == (failStore ? -1 : 1));
    assert(g_mDoMemCd_control.SaveSync() == (failStore ? 2 : 1));
    // Observation did not consume completion or invent another store.
    assert(stores == 1);
    COSSdkRequestShutdown();
    std::_Exit(0); // SDK card worker is process-lifetime, as in the game.
}
