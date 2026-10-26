// Simulate only the external VideoOut/clock service. Exercise the real recorder.
#include "frame-pacing.hpp"
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <mutex>
#include <thread>

namespace {
std::mutex serviceMutex;
uint64_t count = 0, tick = 0;
std::atomic<uint64_t> seen{0}, polls{0};
void complete(uint64_t number, uint64_t time) {
    {
        std::lock_guard lock(serviceMutex);
        count = number; tick = time;
    }
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(2);
    while (seen < number && std::chrono::steady_clock::now() < deadline) std::this_thread::sleep_for(std::chrono::milliseconds(1));
    assert(seen >= number);
    (void)pswaker_perf_status(); // Public snapshot waits for the observation's export.
}
void present(uint64_t frame, uint64_t argument, uint64_t time) {
    if (frame) pswaker_perf_game_frame(frame);
    pswaker_perf_present(pswaker_perf_capture());
    extern int submit(uint64_t);
    assert(submit(argument) == 0);
    complete(argument, time);
}
}
extern "C" int __wrap_sceVideoOutSubmitFlip(int, int, uint32_t, int64_t);
namespace { int submit(uint64_t arg) { return __wrap_sceVideoOutSubmitFlip(1, 0, 1, arg); } }
#if defined(PSWAKER_TEST_PLATFORM_LOGGER)
extern "C" void say(const char*, ...);
extern "C" int sceKernelDebugOutText(int, const char*) {
    // The external debugger consumes ten milliseconds per line. Use the fake
    // display clock rather than host wall time to keep the regression exact.
    std::lock_guard lock(serviceMutex);
    tick += 10;
    return 0;
}
#endif
extern "C" uint64_t sceKernelGetTscFrequency() { return 1000; }
extern "C" uint64_t sceKernelReadTsc() { std::lock_guard lock(serviceMutex); return tick + 1; }
extern "C" int __real_sceVideoOutSubmitFlip(int, int, uint32_t, int64_t) { return 0; }
extern "C" int sceVideoOutGetFlipStatus(int, void* output) {
    std::lock_guard lock(serviceMutex);
    std::memset(output, 0, 64);
    auto* fields = static_cast<uint64_t*>(output);
    fields[0] = count; fields[1] = tick * 1000; fields[2] = tick; fields[3] = count;
    seen = count; ++polls;
    return 0;
}
int main(int argc, char** argv) {
    assert(argc == 3);
    pswaker_perf_initialize("synthetic", argv[1]);
    pswaker_perf_stage("sea", 44);
    pswaker_perf_arm("outset");
#if defined(PSWAKER_TEST_PLATFORM_LOGGER)
    if (!strcmp(argv[2], "diagnostics")) {
        present(1, 1, 1000);
        // The real native say() path used by the periodic heartbeat. Its FTP
        // file/stdout evidence must remain while the unused debugger is slow.
        for (int i = 0; i < 7; ++i) say("heartbeat-evidence-%d", i);
        uint64_t next;
        { std::lock_guard lock(serviceMutex); next = tick + 33; }
        present(2, 2, next);
        pswaker_perf_shutdown();
        return 0;
    }
#endif
    if (!strcmp(argv[2], "ui")) {
        pswaker_perf_shader_wait(pswaker_perf_now() - 40000000);
        present(0, 1, 1000); // Armed menu frame remains outside gameplay.
        pswaker_perf_pause(); // Arming in a paused menu must survive until resume.
        pswaker_perf_game_frame(1);
        pswaker_perf_shader_wait(pswaker_perf_now() - 40000000);
        present(1, 2, 2000);
        present(2, 3, 122000);
        pswaker_perf_shutdown();
        return 0;
    }
    present(1, 1, 1000);
    if (!strcmp(argv[2], "diagnostic-cost")) {
        pswaker_perf_diagnostic(PswakerDiagnostic::Heartbeat, pswaker_perf_now() - 44000000);
        pswaker_perf_diagnostic(PswakerDiagnostic::Input, pswaker_perf_now() - 10000000);
        present(2, 2, 121000);
        pswaker_perf_shutdown();
        return 0;
    }
    if (!strcmp(argv[2], "pause")) {
        pswaker_perf_pause();
        pswaker_perf_stage("A_mori", 0);
        pswaker_perf_arm("forest");
        present(2, 2, 2000);
        present(3, 3, 122000);
        pswaker_perf_shutdown();
        return 0;
    }
    if (!strcmp(argv[2], "missing")) {
        pswaker_perf_game_frame(2);
        pswaker_perf_present(pswaker_perf_capture());
        assert(submit(2) == 0);
        present(3, 3, 121000); // Completion 2 was never observed.
        pswaker_perf_shutdown();
        return 0;
    }
    const auto before = polls.load();
    while (polls < before + 5) std::this_thread::sleep_for(std::chrono::milliseconds(1));
    pswaker_perf_shader_wait(pswaker_perf_now() - 40000000);
    present(2, 2, 2000);
    present(3, 3, 121000); // Retain the whole long interval across the 120s boundary.
    present(0, 4, 121001); // A port screen is not a game frame.
    pswaker_perf_shutdown();
}
