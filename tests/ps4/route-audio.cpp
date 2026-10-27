#include <cos_sdk/audio.h>
#include <cos_sdk/hooks.h>
#include <dolphin/ai.h>
#include <aurora/aurora.h>
#include <SDL3/SDL.h>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <thread>

namespace aurora { AuroraConfig g_config{}; }
extern "C" { uintptr_t OSBaseAddress = 0; }
void* MEM1Start = nullptr;
void* MEM1End = nullptr;
namespace {
alignas(32) uint8_t memory[64]{};
std::atomic<unsigned> callbacks{0}, delivered{0}, destroyed{0};
std::atomic<unsigned> formats{0};
const char* scenario = "pcm";
bool mode(const char* name) { return !std::strcmp(scenario, name); }
void interrupt() { ++callbacks; }
}
extern "C" {
bool SDL_InitSubSystem(SDL_InitFlags) { return true; }
const char* SDL_GetError() { return "injected SDL failure"; }
const char* SDL_GetCurrentAudioDriver() { return "test-boundary"; }
SDL_AudioStream* SDL_OpenAudioDeviceStream(SDL_AudioDeviceID, const SDL_AudioSpec* spec,
                                         SDL_AudioStreamCallback, void*) {
    assert(spec->freq == 32000 && spec->channels == 2 && spec->format == SDL_AUDIO_S16);
    return reinterpret_cast<SDL_AudioStream*>(uintptr_t(1));
}
bool SDL_ResumeAudioStreamDevice(SDL_AudioStream*) { return true; }
bool SDL_SetAudioStreamFormat(SDL_AudioStream*, const SDL_AudioSpec* spec, const SDL_AudioSpec*) {
    assert(spec->freq == 48000 && spec->channels == 2 && spec->format == SDL_AUDIO_S16);
    return ++formats != 1; // First change fails, and must be retried.
}
int SDL_GetAudioStreamQueued(SDL_AudioStream*) {
    if (mode("drops") && !COSSdkIsShuttingDown()) return 25600; // 200 ms at 32 kHz
    if (mode("queue-error")) return -1;
    return 0;
}
int SDL_GetAudioStreamAvailable(SDL_AudioStream*) { return 0; }
bool SDL_FlushAudioStream(SDL_AudioStream*) { return !mode("drain-error"); }
void SDL_DestroyAudioStream(SDL_AudioStream*) { ++destroyed; }
bool SDL_PutAudioStreamData(SDL_AudioStream*, const void* data, int bytes) {
    assert(!destroyed);
    const auto* samples = static_cast<const int16_t*>(data);
    for (int i = 0; i < bytes / 2; i += 2) {
        assert(samples[i] == 0x1234); // left from bytes 2/3
        assert(samples[i+1] == -2);   // right from bytes 0/1
    }
    ++delivered;
    return true;
}
}
int main(int argc, char** argv) {
    assert(argc == 2);
    scenario = argv[1];
    for (unsigned i = 0; i < sizeof memory; i += 4) {
        memory[i] = 0xff; memory[i+1] = 0xfe;
        memory[i+2] = 0x12; memory[i+3] = 0x34;
    }
    OSBaseAddress = reinterpret_cast<uintptr_t>(memory);
    MEM1Start = memory;
    MEM1End = memory + sizeof memory;
    aurora::g_config.mem1Size = sizeof memory;
    // Hold the SDK interrupt lock until the registers/callback are all installed.
    const BOOL enabled = OSDisableInterrupts();
    AIInit(nullptr);
    AIRegisterDMACallback(interrupt);
    AIInitDMA(0, sizeof memory);
    AIStartDMA();
    OSRestoreInterrupts(enabled);
    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(3);
    COSAIPlaybackStats stats{};
    while (std::chrono::steady_clock::now() < deadline) {
        COSAIGetPlaybackStats(&stats);
        if ((mode("drops") && stats.queueDrops >= 3) ||
            (mode("queue-error") && stats.outputErrors >= 3) || delivered >= 3) break;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    assert(callbacks > 0);
    if (mode("format")) {
        AISetDSPSampleRate(AI_SAMPLERATE_48KHZ);
        while (formats < 2 && std::chrono::steady_clock::now() < deadline)
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        assert(formats >= 2);
    }
    COSSdkRequestShutdown();
    assert(COSAIShutdownOutput());
    assert(destroyed == 1);
    const unsigned completed = delivered;
    std::this_thread::sleep_for(std::chrono::milliseconds(5));
    assert(delivered == completed);
    COSAIGetPlaybackStats(&stats);
    assert(stats.sourceHz == (mode("format") ? 48000 : 32000));
    if (mode("drops")) {
        assert(stats.queueDrops >= 3 && stats.droppedFrames >= 24 && delivered == 0);
    } else if (mode("queue-error")) {
        assert(stats.outputErrors >= 3 && delivered == 0);
    } else {
        assert(delivered >= 3);
        assert(stats.outputErrors == (mode("format") || mode("drain-error") ? 1 : 0));
    }
}
