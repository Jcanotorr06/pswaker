// The five worker loop bodies are inserted verbatim from the prepared game.
// Queue/thread/shutdown operations use the real SDK. Asset decoding, ARAM I/O,
// exception display, audio mixing and class construction are outside this lifecycle
// seam. A dispatch after shutdown can only come from a receive that delivered nothing.
#include <dolphin/os.h>
#include <cos_sdk/hooks.h>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iterator>
#include <thread>
#include <sys/resource.h>

#define ARRAY_SIZE(array) std::size(array)
#define JUT_ASSERT(line, condition) assert(condition)
#define OSReport(...) ((void)0)
static std::atomic<unsigned> processed{0};
static void dispatched() {
    if (COSSdkIsShuttingDown()) std::abort();
    ++processed;
}

struct JKRAramStreamCommand { enum { READ = 1, WRITE = 2 }; int mType = WRITE; };
struct JKRAramStream {
    static inline OSMessageQueue sMessageQueue{};
    static inline OSMessage sMessageBuffer[4]{};
    void* run();
    int readFromAram() { std::abort(); }
    int writeToAram(JKRAramStreamCommand*) { ++processed; return 1; }
};
struct JKRAMCommand {};
struct JKRAramPiece {
    struct Message { s32 field_0x00; JKRAMCommand* command; };
    static void sendCommand(void*) { std::abort(); }
    static void startDMA(JKRAMCommand*) { dispatched(); }
};
struct JKRAram {
    static inline OSMessageQueue sMessageQueue{};
    static inline OSMessage sMessageBuffer[4]{};
    void* run();
};
struct JKRDecompCommand {
    u8* mSrcBuffer = nullptr;
    u8* mDstBuffer = nullptr;
    u32 mSrcLength = 0, mDstLength = 0;
    int field_0x20 = 0;
    void* mAMCommand = nullptr;
    void (*mCallback)(uintptr_t) = [](uintptr_t) { ++processed; };
    OSMessageQueue* field_0x1c = nullptr;
    OSMessageQueue mMessageQueue{};
};
struct JKRDecomp {
    static inline OSMessageQueue sMessageQueue{};
    static inline OSMessage sMessageBuffer[4]{};
    void* run();
    void decode(u8*, u8*, u32, u32) {}
};
using JUTExceptionUserCallback = void (*)(u16, OSContext*, int, int);
struct CallbackObject {
    JUTExceptionUserCallback callback = nullptr;
    u16 error = 0;
    OSContext* context = nullptr;
    int param_3 = 0, param_4 = 0;
};
struct JUTExternalFB {};
struct DirectPrint {
    JUTExternalFB frame;
    void* getFrameBuffer() { return &frame; }
};
struct JUTException {
    static inline OSMessageQueue sMessageQueue{};
    static inline OSMessage sMessageBuffer[1]{};
    static inline JUTException* sErrorManager = nullptr;
    DirectPrint print;
    DirectPrint* mDirectPrint = &print;
    JUTExternalFB* mFrameMemory = nullptr;
    void* run();
    void createFB() { std::abort(); }
    void printContext(u16, OSContext*, int, int) {
        ++processed;
        OSEnableInterrupts(); // The real exception display never returns.
    }
};
static u32 PPCMfmsr() { return 0; }
static void PPCMtmsr(u32) {}
struct JKRThread { JKRThread(OSThread*, int) {} };
static void DspBoot(void (*)(u16)) {}
static void AISetDSPSampleRate(int) {}
static void AIRegisterDMACallback(void (*)()) {}
static void AIStartDMA() {}
static OSMessageQueue sAudioStartedMQ;
static OSMessage sAudioStartedMsg;
namespace JASystem {
namespace Kernel {
static void init() {}
static int getAiSetting() { return 0; }
static void updateDac() { dispatched(); }
static void probeStart(int, char*) {}
static void probeFinish(int) {}
}
namespace TDSP_DACBuffer {
static void init() {}
static void updateDSP() {}
static void finishDSPFrame() {}
}
namespace Driver { static void init() {} }
struct TAudioThread {
    static inline OSThread sAudioThread{};
    static inline OSMessageQueue sAudioprocMQ{};
    static inline OSMessage saAudioMsgBuf[16]{};
    static inline u32 sAudioprocMQInit = 0;
    static inline int sbIsDSPBoot = 0;
    static inline vs32 snIntCount = 0;
    static void syncDSP(u16) {}
    static void syncAudio() {}
    static void* audioproc(void*);
};
}

// WORKER_METHODS

template<class Predicate> void waitFor(Predicate predicate) {
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (!predicate() && std::chrono::steady_clock::now() < deadline)
        std::this_thread::yield();
    assert(predicate());
}

static JKRAramStream aram;
static JKRDecomp decomp;
static JUTException exception;
static JKRAram piece;
constexpr int workerCount = 5;
static OSThread workers[workerCount];
static bool enabled[workerCount] = {true, true, true, true, true};
alignas(32) static u8 stacks[workerCount][16384];

static void* runAram(void*) { return aram.run(); }
static void* runDecomp(void*) { return decomp.run(); }
static void* runException(void*) { return exception.run(); }
static void* runPiece(void*) { return piece.run(); }
static void* runAudio(void*) { return JASystem::TAudioThread::audioproc(nullptr); }

static bool waiting() {
    const BOOL interrupts = OSDisableInterrupts();
    bool result = true;
    for (int i = 0; i < workerCount; ++i)
        if (enabled[i]) result = result && workers[i].state == OS_THREAD_STATE_WAITING;
    OSRestoreInterrupts(interrupts);
    return result;
}

int main(int argc, char** argv) {
    assert(argc == 2);
    const rlimit noCore{0, 0};
    assert(setrlimit(RLIMIT_CORE, &noCore) == 0);
    OSGetCurrentThread(); // Adopt the process main thread before starting workers.
    JUTException::sErrorManager = &exception;
    OSInitMessageQueue(&sAudioStartedMQ, &sAudioStartedMsg, 1);
    const char* names[] = {"aram", "decomp", "exception", "piece", "audio"};
    if (std::strcmp(argv[1], "idle") && std::strcmp(argv[1], "after-work"))
        for (int i = 0; i < workerCount; ++i) enabled[i] = !std::strcmp(argv[1], names[i]);
    void* (*entries[])(void*) = {runAram, runDecomp, runException, runPiece, runAudio};
    bool selected = false;
    for (int i = 0; i < workerCount; ++i) {
        if (!enabled[i]) continue;
        selected = true;
        assert(OSCreateThread(&workers[i], entries[i], nullptr, stacks[i] + sizeof stacks[i],
                              sizeof stacks[i], 16, 0));
        OSResumeThread(&workers[i]);
    }
    waitFor(waiting);
    JKRAramStreamCommand aramCommand;
    JKRDecompCommand decompCommand;
    CallbackObject exceptionCommand;
    JKRAMCommand pieceCommand;
    if (!std::strcmp(argv[1], "after-work")) {
        // Holding the SDK lock makes all five real commands pending together.
        const BOOL interrupts = OSDisableInterrupts();
        assert(OSSendMessage(&aram.sMessageQueue, &aramCommand, OS_MESSAGE_NOBLOCK));
        assert(OSSendMessage(&decomp.sMessageQueue, &decompCommand, OS_MESSAGE_NOBLOCK));
        assert(OSSendMessage(&exception.sMessageQueue, &exceptionCommand, OS_MESSAGE_NOBLOCK));
        assert(OSSendMessage(&piece.sMessageQueue, new JKRAramPiece::Message{1, &pieceCommand},
                             OS_MESSAGE_NOBLOCK));
        assert(OSSendMessage(&JASystem::TAudioThread::sAudioprocMQ, nullptr, OS_MESSAGE_NOBLOCK));
        OSRestoreInterrupts(interrupts);
        waitFor([] { return processed == 5; });
        waitFor(waiting);
    }
    std::fputs("requesting SDK shutdown with real workers\n", stderr);
    COSSdkRequestShutdown();
    assert(selected);
    for (int i = 0; i < workerCount; ++i)
        if (enabled[i]) assert(OSJoinThread(&workers[i], nullptr));
    std::puts("PASS: selected worker loops ended and joined after SDK shutdown");
}
