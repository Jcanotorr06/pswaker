#include "game-platform.hpp"
#include "native/platform.h"
#include <cos_sdk/audio.h>
#include <atomic>
#include <cstdint>

namespace {
std::atomic<uint64_t> outputCalls{0}, outputErrors{0}, drainErrors{0};
std::atomic<int> lastError{0};
}

// Observe the selected SDL backend without replacing its blocking output or
// conversion. There is no documented underrun counter in the pinned PS4 ABI.
extern "C" int __real_sceAudioOutOutput(int handle, const void* samples);
extern "C" int __wrap_sceAudioOutOutput(int handle, const void* samples) {
    const int result = __real_sceAudioOutOutput(handle, samples);
    if (samples) ++outputCalls;
    if (result < 0) {
        if (samples) ++outputErrors;
        else ++drainErrors;
        lastError = result;
    }
    return result;
}

void pswaker_log_audio_output() {
    COSAIPlaybackStats stats{};
    COSAIGetPlaybackStats(&stats);
    say("AUDIO_OUTPUT source-hz=%u queued-source-bytes=%d queue-drops=%llu dropped-frames=%llu "
        "clock-skips=%llu skipped-frames=%llu stream-errors=%llu backend-calls=%llu "
        "backend-errors=%llu backend-drain-errors=%llu last-backend-error=0x%08x "
        "hardware-underruns=unsupported; software counters do not prove audible correctness",
        stats.sourceHz, stats.queuedBytes, (unsigned long long)stats.queueDrops,
        (unsigned long long)stats.droppedFrames, (unsigned long long)stats.clockSkips,
        (unsigned long long)stats.skippedFrames, (unsigned long long)stats.outputErrors,
        (unsigned long long)outputCalls.load(), (unsigned long long)outputErrors.load(),
        (unsigned long long)drainErrors.load(), unsigned(lastError.load()));
}
