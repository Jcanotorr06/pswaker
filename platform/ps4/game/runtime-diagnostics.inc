// PS4 uses the selected DolphinPS4 crash logger; no foreign ucontext layout or recovery.
#include "pc_internal.h"
#include "game-platform.hpp"
#include "frame-pacing.hpp"
#include <atomic>
#include <algorithm>
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <mutex>
#include <unistd.h>

namespace pc {
namespace {
std::atomic<int> scene{-1};
std::atomic<unsigned> resources{0};
char lastResource[256]{};
std::mutex resourceMutex;
}
void writef(int fd, const char* format, ...) {
    char text[2048];
    va_list args;
    va_start(args, format);
    const int length = vsnprintf(text, sizeof text, format, args);
    va_end(args);
    if (length <= 0) return;
    size_t remaining = std::min(size_t(length), sizeof text - 1);
    const char* cursor = text;
    while (remaining) {
        const auto written = write(fd, cursor, remaining);
        if (written <= 0) break;
        cursor += written;
        remaining -= written;
    }
}
int openRunFile(const char* name) {
    char path[512];
    snprintf(path, sizeof path, "/data/pswaker/logs/%s", name);
    return open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
}
const char* traceSceneName(int id) {
    static const char* names[] = {"OVERLAP0", "OVERLAP1", "OVERLAP6", "OVERLAP7", "OVERLAP8",
        "LOGO_SCENE", "MENU_SCENE", "PLAY_SCENE", "OPENING_SCENE", "OPENING2_SCENE", "TITLE_SCENE",
        "ENDING_SCENE", "NAME_SCENE", "NAMEEX_SCENE", "OPEN_SCENE", "OPEN2_SCENE", "OVERLAP2",
        "OVERLAP3", "OVERLAP4", "OVERLAP5", "ROOM_SCENE"};
    return id >= 0 && id < 21 ? names[id] : "unknown";
}
int traceScene() { return scene.load(); }
unsigned traceResourceCount() { return resources.load(); }
void traceLastResource(char* out, size_t size) {
    std::lock_guard lock(resourceMutex);
    if (size) snprintf(out, size, "%s", lastResource);
}
void writeState(int fd) {
    std::lock_guard lock(resourceMutex);
    writef(fd, "scene=%s(%d) frame=%u last_resource=%s resources=%u ms=%llu\n",
        traceSceneName(scene), int(scene), pc_frame_count(), lastResource, unsigned(resources),
        (unsigned long long)elapsedMs());
}
void installCrashHandler() { pswaker_stage("PS4-runtime-crash-logger-selected"); }
void dumpAllThreads(int fd) { writeState(fd); }
}
extern "C" int pc_trace_enabled(const char* channel) {
    const char* list = pc::gConfig.trace;
    if (!list) return 0;
    const size_t length = strlen(channel);
    for (const char* cursor = list; *cursor;) {
        const char* end = strchr(cursor, ',');
        const size_t count = end ? size_t(end-cursor) : strlen(cursor);
        if ((length == count && !strncmp(cursor, channel, count)) ||
            (count == 3 && !strncmp(cursor, "all", 3))) return 1;
        if (!end) break;
        cursor = end+1;
    }
    return 0;
}
extern "C" void pc_trace_scene(int id) {
    pswaker_perf_scene_request(pc::traceSceneName(id));
    static uint64_t previousMs = 0;
    const auto now = pc::elapsedMs();
    pc::scene = id;
    pc::writef(STDERR_FILENO, "SCENE create-request ms=%llu previous_request_interval_ms=%llu name=%s id=%d frame=%u; visible completion needs owner observation\n",
        (unsigned long long)now, (unsigned long long)(now-previousMs), pc::traceSceneName(id), id, pc_frame_count());
    previousMs = now;
}
extern "C" void pc_trace_resource(const char* path, int) {
    std::lock_guard lock(pc::resourceMutex);
    snprintf(pc::lastResource, sizeof pc::lastResource, "%s", path ? path : "?");
    ++pc::resources;
}
extern "C" void pswaker_log_game_state() { pc::writeState(STDERR_FILENO); }
extern "C" void pc_panic(const char* file, int line) {
    pc::writef(STDERR_FILENO, "PANIC %s:%d\n", file, line);
    pc::writeState(STDERR_FILENO);
    pswaker_exit(12);
}
