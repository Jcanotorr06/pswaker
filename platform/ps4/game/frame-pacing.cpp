#include "frame-pacing.hpp"
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <mutex>
#include <thread>
#include <unistd.h>
#include <vector>
#if defined(__ORBIS__)
#include <dolphin/types.h>
class JKRHeap;
#include "pc/game_hooks/jkr_heap.h"
#endif

// Same 64-byte ABI as the selected Mesa wsi_common_videoout.c and OpenOrbis.
// Keep raw timestamp fields: their interpretation must be checked on hardware.
struct FlipStatus {
    uint64_t count, processTime, tsc;
    int64_t argument;
    uint64_t reserved[2];
    int32_t gpuPending, pending, buffer;
    uint32_t reserved1;
};
static_assert(sizeof(FlipStatus) == 64);
extern "C" int sceVideoOutGetFlipStatus(int, FlipStatus*);
extern "C" uint64_t sceKernelGetTscFrequency();
extern "C" uint64_t sceKernelReadTsc();
extern "C" int __real_sceVideoOutSubmitFlip(int, int, uint32_t, int64_t);

namespace {
std::mutex mutex;
std::atomic<bool> stopping{false};
std::thread observer;
std::atomic<uint64_t> gameFrame{0}, shaderNs{0}, shaderCalls{0};
unsigned activeSample = 0, sequence = 0;
FILE *frames = nullptr, *events = nullptr, *summaries = nullptr;
// Only this worker touches the evidence streams during gameplay. Producers
// copy bounded rows; a slow disk cannot hold the frame/submission state lock.
class EvidenceWriter {
    struct Row {
        FILE* file = nullptr;
        char text[512]{};
        bool durable = false;
        unsigned sample = 0;
    };
    std::array<Row, 1024> rows{};
    std::mutex queueMutex;
    std::condition_variable ready;
    std::thread worker;
    size_t head = 0, size = 0;
    bool closing = false;
    std::atomic<bool> failed{false};
    void run() {
        bool reported = false;
        for (;;) {
            Row row;
            {
                std::unique_lock lock(queueMutex);
                ready.wait(lock, [&] { return size || closing; });
                if (!size) break;
                row = rows[head]; head = (head + 1) % rows.size(); --size;
            }
            if (row.file) {
                if (fputs(row.text, row.file) < 0) failed = true;
            } else {
                const auto start = pswaker_perf_now();
                for (auto* file : {frames, events, summaries}) {
                    if (fflush(file)) failed = true;
                    if (row.durable && fsync(fileno(file))) failed = true;
                }
                if (fprintf(events, "%llu,diagnostic-recorder-flush-ns,%llu,%u\n",
                    (unsigned long long)pswaker_perf_now(),
                    (unsigned long long)(pswaker_perf_now() - start), row.sample) < 0) failed = true;
            }
            if (failed && !reported) {
                fprintf(events, "%llu,invalid,evidence-writer,0\n", (unsigned long long)pswaker_perf_now());
                reported = true;
            }
        }
    }
    bool enqueue(const Row& row) {
        std::lock_guard lock(queueMutex);
        if (size == rows.size() || closing) { failed = true; return false; }
        rows[(head + size) % rows.size()] = row;
        ++size; ready.notify_one(); return true;
    }
public:
    void start() { worker = std::thread([this] { run(); }); }
    bool bad() const { return failed; }
    template <typename... Args> bool append(FILE* file, const char* format, Args... args) {
        Row row; row.file = file;
        const int length = snprintf(row.text, sizeof row.text, format, args...);
        if (length < 0 || size_t(length) >= sizeof row.text) { failed = true; return false; }
        return enqueue(row);
    }
    bool flush(bool durable, unsigned sampleId) {
        Row row; row.durable = durable; row.sample = sampleId;
        return enqueue(row);
    }
    void drain() {
        { std::lock_guard lock(queueMutex); closing = true; ready.notify_one(); }
        if (worker.joinable()) worker.join();
    }
} writer;
char directory[256]{}, statusText[256] = "No performance sample requested.";
char stageName[64] = "unknown";
int roomNumber = -1, videoHandle = -1;
uint64_t frequency = 0, lastCount = 0, lastTick = 0;
bool haveStatus = false, broken = false;
struct Present {
    PswakerFrameTag tag;
    uint64_t submitNs, shaderNs, shaderCalls;
    int64_t argument;
    char stage[64];
    int room;
};
std::deque<Present> queued, submitted;
struct Sample {
    unsigned id = 0;
    char scene[16]{};
    uint64_t firstTick = 0, lastTick = 0, lastFrame = 0;
    uint64_t resumeNs = 0, lastShaderNs = 0;
    unsigned shaderHitches = 0;
    std::vector<double> intervals;
} sample;

void fail(const char* reason);
void event(const char* kind, const char* detail, unsigned sampleId = ~0u) {
    if (events && !writer.append(events, "%llu,%s,%s,%u\n", (unsigned long long)pswaker_perf_now(),
                          kind, detail, sampleId == ~0u ? activeSample : sampleId)) fail("evidence-writer");
}
void fail(const char* reason) {
    if (broken) return;
    broken = true;
    event("invalid", reason);
    snprintf(statusText, sizeof statusText, "Timing unavailable: %s. Retain this launch's logs.", reason);
}
double percentile(const std::vector<double>& sorted, double fraction) {
    return sorted[static_cast<size_t>(std::ceil(fraction * sorted.size())) - 1];
}
void finish(const char* outcome) {
    if (!sample.id) return;
#if defined(__ORBIS__)
    JKRPcHostAllocScope hostAlloc;
#endif
    auto sorted = sample.intervals;
    std::sort(sorted.begin(), sorted.end());
    const double seconds = frequency && sample.lastTick > sample.firstTick ?
        double(sample.lastTick - sample.firstTick) / frequency : 0;
    const double fps = seconds ? sorted.size() / seconds : 0;
    const double p95 = sorted.empty() ? 0 : percentile(sorted, .95);
    const double p99 = sorted.empty() ? 0 : percentile(sorted, .99);
    const double maximum = sorted.empty() ? 0 : sorted.back();
    const bool complete = !strcmp(outcome, "complete") && !broken;
    const bool target = complete && seconds >= 120 && fps >= 29.5 && p95 <= 35 && p99 <= 50 && maximum <= 100;
    if (summaries) {
        if (!writer.append(summaries, "%u,%s,%s,%.6f,%zu,%.6f,%.6f,%.6f,%.6f,%u,%d\n", sample.id,
            sample.scene, broken ? "invalid" : outcome, seconds, sorted.size(), fps, p95, p99, maximum,
            sample.shaderHitches, target)) fail("summary-write");
    }
    snprintf(statusText, sizeof statusText, "Sample %u (%s): %s; %.2f FPS, p95 %.2f, p99 %.2f, max %.2f ms. Retrieve logs.",
        sample.id, sample.scene, broken ? "invalid" : outcome, fps, p95, p99, maximum);
    event("sample-end", broken ? "invalid" : outcome);
    activeSample = 0;
    sample = {};
    if (!writer.flush(true, 0)) fail("evidence-writer");
}
void observe(const FlipStatus& flip, uint64_t observed, uint64_t readTick) {
    if (haveStatus && flip.count == lastCount) {
        if (flip.tsc != lastTick) fail("timestamp-changed-without-completion");
        return; // Repeated scanout is not a new game frame.
    }
    if (haveStatus && flip.count != lastCount + 1) fail("missed-flip-completion");
    if (!haveStatus && flip.count != 1) fail("missed-initial-flip");
    if (!flip.tsc || (haveStatus && flip.tsc <= lastTick)) fail("nonmonotonic-flip-clock");
    if (!frequency || readTick < flip.tsc)
        fail("unverified-flip-clock-domain");
    else if (double(readTick - flip.tsc) / frequency > .100) {
        char text[32];
        snprintf(text, sizeof text, "%llu", (unsigned long long)(1e9 * double(readTick - flip.tsc) / frequency));
        event("observer-delay-ns", text);
    }
    haveStatus = true; lastCount = flip.count; lastTick = flip.tsc;
    while (!submitted.empty() && submitted.front().argument < flip.argument) {
        fail("unobserved-submitted-frame"); submitted.pop_front();
    }
    if (submitted.empty() || submitted.front().argument != flip.argument) {
        fail("unmapped-flip-completion"); return;
    }
    const auto present = submitted.front(); submitted.pop_front();
    if (frames && !writer.append(frames, "%llu,%llu,%llu,%llu,%lld,%llu,%u,%s,%d,%llu,%llu,%llu,%llu\n",
        (unsigned long long)flip.count, (unsigned long long)flip.processTime, (unsigned long long)flip.tsc,
        (unsigned long long)observed, (long long)flip.argument, (unsigned long long)present.tag.frame,
        present.tag.sample, present.stage, present.room, (unsigned long long)present.submitNs,
        (unsigned long long)present.shaderNs, (unsigned long long)present.shaderCalls,
        (unsigned long long)readTick)) fail("frames-write");
    if (!sample.id || present.tag.sample != sample.id) return;
    if (!present.tag.frame || (sample.lastFrame && present.tag.frame != sample.lastFrame + 1)) fail("nonconsecutive-game-frame");
    if (sample.firstTick) {
        const double interval = 1000.0 * (flip.tsc - sample.lastTick) / frequency;
        sample.intervals.push_back(interval);
        // Correlation, not proof that shader work caused the whole interval.
        if (interval > 35 && present.shaderNs - sample.lastShaderNs >= 1000000) ++sample.shaderHitches;
    } else {
        sample.firstTick = flip.tsc;
        event("sample-first-presentation", sample.scene);
    }
    sample.lastTick = flip.tsc; sample.lastFrame = present.tag.frame; sample.lastShaderNs = present.shaderNs;
    if (frequency && double(sample.lastTick - sample.firstTick) / frequency >= 120) finish("complete");
}
void poll() {
    unsigned polls = 0;
    while (!stopping) {
        {
            std::lock_guard lock(mutex);
            if (writer.bad()) fail("evidence-writer");
            if (videoHandle >= 0) {
                FlipStatus flip{};
                if (sceVideoOutGetFlipStatus(videoHandle, &flip)) fail("flip-status-unavailable");
                else if (flip.count) observe(flip, pswaker_perf_now(), sceKernelReadTsc());
            }
            if (++polls % 1000 == 0) {
                if (!writer.flush(false, activeSample)) fail("evidence-writer");
            }
        }
        usleep(1000);
    }
}
}
extern "C" uint64_t pswaker_perf_now() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
void pswaker_perf_diagnostic(PswakerDiagnostic kind, uint64_t start) {
    const auto duration = pswaker_perf_now() - start;
    std::lock_guard lock(mutex);
    char text[32]; snprintf(text, sizeof text, "%llu", (unsigned long long)duration);
    event(kind == PswakerDiagnostic::Input ? "diagnostic-input-ns" : "diagnostic-heartbeat-ns", text,
          sample.resumeNs ? activeSample : 0);
}
void pswaker_perf_initialize(const char* build, const char* logsRoot) {
    const int length = snprintf(directory, sizeof directory, "%s/performance-XXXXXX", logsRoot);
    if (length < 0 || size_t(length) >= sizeof directory) { fail("run-path-too-long"); return; }
    if (!mkdtemp(directory)) { fail("create-run-directory"); return; }
    const auto open = [](const char* name) {
        char path[512]; snprintf(path, sizeof path, "%s/%s", directory, name); return fopen(path, "wx");
    };
    frames = open("frames.csv"); events = open("events.csv"); summaries = open("samples.csv");
    frequency = sceKernelGetTscFrequency();
    if (!frames || !events || !summaries || !frequency) { fail("open-evidence-or-frequency"); return; }
    fprintf(frames, "flip_count,process_time,tsc,observed_ns,flip_argument,game_frame,sample,stage,room,submit_ns,shader_ns,shader_calls,read_tsc\n");
    fprintf(events, "monotonic_ns,kind,detail,sample\n");
    fprintf(summaries, "sample,scene,outcome,seconds,intervals,average_fps,p95_ms,p99_ms,maximum_ms,shader_correlated_hitches,target_met\n");
    if (FILE* identity = open("identity.json")) {
        const int result = fprintf(identity, "{\"schema\":1,\"build\":\"%s\",\"tsc_frequency\":%llu,\"method\":\"VideoOut-completed-flip-tsc\",\"platform\":\"owner-confirm-required\",\"cache\":\"/data/pswaker/cache/%s\",\"internal\":[1280,720],\"logic_hz\":30,\"textures\":\"stock\"}\n", build, (unsigned long long)frequency, build);
        bool good = result > 0 && fflush(identity) == 0;
        if (fsync(fileno(identity))) good = false;
        if (fclose(identity)) good = false;
        if (!good) fail("identity-write");
    } else fail("identity-open");
    writer.start();
    event("phase", "startup");
    observer = std::thread(poll);
}
void pswaker_perf_shutdown() {
    stopping = true;
    if (observer.joinable()) observer.join();
    {
        std::lock_guard lock(mutex);
        if (writer.bad()) fail("evidence-writer");
        finish("interrupted"); event("shutdown", "complete");
    }
    writer.drain();
    for (auto* file : {frames, events, summaries}) if (file) {
        bool good = fflush(file) == 0;
        if (fsync(fileno(file))) good = false;
        if (fclose(file)) good = false;
        if (!good) broken = true;
    }
    frames = events = summaries = nullptr;
}
void pswaker_perf_arm(const char* scene) {
    std::lock_guard lock(mutex);
    finish("interrupted");
    if (broken || !frames || (strcmp(scene, "outset") && strcmp(scene, "forest"))) return;
    sample.id = activeSample = ++sequence;
    snprintf(sample.scene, sizeof sample.scene, "%s", scene);
    event("phase", "gameplay"); event("sample-arm", scene);
    snprintf(statusText, sizeof statusText, "Sample %u (%s) armed. Resume; play for two minutes without pausing or leaving this scene.", sample.id, scene);
}
void pswaker_perf_game_frame(uint64_t frame) {
    std::lock_guard lock(mutex);
    gameFrame = frame;
    if (sample.id && !sample.resumeNs) {
        sample.resumeNs = pswaker_perf_now();
        event("sample-resume", sample.scene);
    }
}
void pswaker_perf_pause() {
    std::lock_guard lock(mutex);
    // Arming happens inside the paused menu; don't cancel before its first frame.
    if (sample.firstTick) finish("paused");
}
void pswaker_perf_phase(const char* phase) {
    std::lock_guard lock(mutex);
    if (strcmp(phase, "gameplay") && sample.id) finish("phase-change");
    event("phase", phase);
}
void pswaker_perf_stage(const char* stage, int room) {
    std::lock_guard lock(mutex);
    if (sample.id) finish("stage-change");
    snprintf(stageName, sizeof stageName, "%s", stage); roomNumber = room;
    event("stage", stageName);
}
void pswaker_perf_scene_request(const char* scene) { std::lock_guard lock(mutex); event("scene-request", scene); }
const char* pswaker_perf_status() {
    static thread_local char copy[256];
    std::lock_guard lock(mutex);
    if (writer.bad()) fail("evidence-writer");
    snprintf(copy, sizeof copy, "%s", statusText); return copy;
}
extern "C" PswakerFrameTag pswaker_perf_capture() {
    std::lock_guard lock(mutex);
    const auto frame = gameFrame.exchange(0);
    PswakerFrameTag tag{frame, frame ? activeSample : 0, {}, roomNumber};
    snprintf(tag.stage, sizeof tag.stage, "%s", stageName);
    return tag;
}
extern "C" void pswaker_perf_present(PswakerFrameTag tag) {
    std::lock_guard lock(mutex);
    if (queued.size() >= 128) { fail("present-queue-overflow"); return; }
    Present present{tag, pswaker_perf_now(), shaderNs.load(), shaderCalls.load(), 0, {}, tag.room};
    snprintf(present.stage, sizeof present.stage, "%s", tag.stage);
    queued.push_back(present);
}
extern "C" void pswaker_perf_present_failed() { std::lock_guard lock(mutex); fail("surface-present-failed"); }
extern "C" void pswaker_perf_shader_wait(uint64_t start) {
    const auto duration = pswaker_perf_now() - start;
    shaderNs += duration; ++shaderCalls;
    std::lock_guard lock(mutex);
    char text[32]; snprintf(text, sizeof text, "%llu", (unsigned long long)duration);
    event("shader-wait-ns", text, sample.resumeNs ? activeSample : 0);
}
extern "C" int __wrap_sceVideoOutSubmitFlip(int handle, int buffer, uint32_t mode, int64_t argument) {
    std::lock_guard lock(mutex);
    const int result = __real_sceVideoOutSubmitFlip(handle, buffer, mode, argument);
    if (result) { fail("submit-flip-failed"); return result; }
    if (videoHandle >= 0 && videoHandle != handle) fail("video-handle-changed");
    videoHandle = handle;
    if (queued.empty()) { fail("untagged-present"); return result; }
    auto present = queued.front(); queued.pop_front(); present.argument = argument;
    if (submitted.size() >= 128) { fail("completion-queue-overflow"); return result; }
    submitted.push_back(present);
    return result;
}
