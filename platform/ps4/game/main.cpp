#include "game-platform.hpp"
#include "installed-content.hpp"
#include "controls.hpp"
#include "native/platform.h"
#include <aurora/event.h>
#include <aurora/gfx.h>
#include <aurora/gfx.hpp>
#include <dolphin/card.h>
#include <dolphin/vi.h>
#include <cos_sdk/audio.h>
#include <cos_sdk/hooks.h>
class JKRHeap;
#include "pc/game_hooks/jkr_heap.h"
#include <SDL3/SDL.h>
#include <imgui.h>
#include "webgpu/gpu.hpp"
#include "window.hpp"
#include <atomic>
#include <chrono>
#include <cerrno>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef PSWAKER_BUILD_ID
#define PSWAKER_BUILD_ID "unrecorded"
#endif
extern "C" int aurora_main(int argc, char** argv);
extern "C" void pswaker_log_game_state();
extern "C" int pswaker_card_shutdown_status();
void pswaker_log_audio_output();
extern "C" uint64_t ps4_disc_busy_until_ns() { return 0; }
namespace {
const auto launch = std::chrono::steady_clock::now();
bool graphics = false;
bool quitting = false;
std::atomic<unsigned> checkedErrors{0};
struct PipelineCounts { uint32_t created, queued; };
PipelineCounts pipelines() {
    const auto* stats = aurora_get_stats();
    return {__atomic_load_n(&stats->createdPipelines, __ATOMIC_RELAXED),
            __atomic_load_n(&stats->queuedPipelines, __ATOMIC_RELAXED)};
}
double milliseconds() {
    return std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now()-launch).count();
}
void events() {
    for (const auto* event = aurora_update(); event && event->type != AURORA_NONE; ++event)
        if (event->type == AURORA_EXIT && !quitting) pswaker_exit(0);
}
enum class Symbol { Cross, Circle, Square, Triangle };
void symbolLine(Symbol symbol, const char* text) {
    // Draw the symbols, rather than relying on optional PlayStation font glyphs.
    const ImVec2 origin = ImGui::GetCursorScreenPos();
    const float size = ImGui::GetTextLineHeight();
    const ImVec2 center(origin.x + size/2, origin.y + size/2);
    const float radius = size * .35f;
    auto* draw = ImGui::GetWindowDrawList();
    const auto color = ImGui::GetColorU32(ImGuiCol_Text);
    if (symbol == Symbol::Circle) draw->AddCircle(center, radius, color, 24, 2);
    else if (symbol == Symbol::Square)
        draw->AddRect(ImVec2(center.x-radius, center.y-radius), ImVec2(center.x+radius, center.y+radius), color, 0, 0, 2);
    else if (symbol == Symbol::Triangle)
        draw->AddTriangle(ImVec2(center.x, center.y-radius), ImVec2(center.x-radius, center.y+radius),
                          ImVec2(center.x+radius, center.y+radius), color, 2);
    else {
        draw->AddLine(ImVec2(center.x-radius, center.y-radius), ImVec2(center.x+radius, center.y+radius), color, 2);
        draw->AddLine(ImVec2(center.x-radius, center.y+radius), ImVec2(center.x+radius, center.y-radius), color, 2);
    }
    ImGui::Dummy(ImVec2(size, size));
    ImGui::SameLine(); ImGui::TextUnformatted(text);
}
void portContent() {
    const auto view = pswaker_port_view();
    if (view.screen == PortScreen::Legend) {
        symbolLine(Symbol::Cross, "Cross = GameCube A");
        symbolLine(Symbol::Circle, "Circle = GameCube B");
        symbolLine(Symbol::Square, "Square = GameCube X");
        symbolLine(Symbol::Triangle, "Triangle = GameCube Y");
        ImGui::TextUnformatted("R1 = Z     Options = Start     Touchpad click = Port settings");
        ImGui::TextUnformatted("Left stick = Control Stick     Right stick = C Stick     D-pad = D-pad");
        ImGui::TextUnformatted("L2 / R2 = analog L / R; terminal click starts at 90% travel.");
        ImGui::TextUnformatted("Original GameCube prompts remain in the game.");
        ImGui::Separator();
        symbolLine(Symbol::Cross, "Continue / Return to settings");
        symbolLine(Symbol::Circle, "Back to settings (when opened from settings)");
    } else if (view.screen == PortScreen::Settings) {
        ImGui::TextUnformatted("D-pad Up / Down: Choose");
        for (unsigned i = 0; i < portMenuItems.size(); ++i)
            ImGui::Text("%s %s", view.selection == i ? ">" : " ", portMenuItems[i].label);
        ImGui::Separator();
        symbolLine(Symbol::Cross, "Confirm"); symbolLine(Symbol::Circle, "Cancel / Resume game");
        ImGui::TextWrapped("The read check resumes gameplay, then pauses after 5 seconds. Hold movement, buttons and triggers during the check; explicitly resume afterward.");
    } else if (view.screen == PortScreen::Quit) {
        ImGui::TextUnformatted("Quit PSWaker?");
        ImGui::TextUnformatted("Only completed in-game saves are retained. Quitting does not save current progress.");
        symbolLine(Symbol::Cross, "Confirm quit"); symbolLine(Symbol::Circle, "Cancel / Back to settings");
    } else if (view.screen == PortScreen::InputLost) {
        ImGui::TextUnformatted("Game paused. Controller disconnected or a controller read failed.");
        ImGui::TextUnformatted(view.connected ? "Controller connected. Release all buttons, sticks and triggers." : "Reconnect your controller to continue.");
        symbolLine(Symbol::Cross, "After releasing all controls, press to resume, then release again.");
        ImGui::TextUnformatted("Reconnection alone does not resume the game.");
    }
    if (view.releasing) ImGui::TextUnformatted("Release all buttons, sticks and triggers to continue.");
}
void screen(const char* title, const char* text, float progress = -1,
            const char* confirm = nullptr, const char* cancel = nullptr) {
    events();
    if (!aurora_begin_frame()) { usleep(16000); return; }
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
    ImGui::Begin("PSWaker", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
                                      ImGuiWindowFlags_NoSavedSettings);
    ImGui::SetWindowFontScale(1.7f);
    ImGui::TextUnformatted(title);
    ImGui::Separator();
    if (text) ImGui::TextWrapped("%s", text);
    else portContent();
    if (progress >= 0) ImGui::ProgressBar(progress, ImVec2(-1, 28));
    if (confirm) symbolLine(Symbol::Cross, confirm);
    if (cancel) symbolLine(Symbol::Circle, cancel);
    ImGui::End();
    aurora_end_frame();
}
void initializeErrorDisplay() {
    if (graphics) return;
    SDL_SetHintWithPriority(SDL_HINT_VIDEO_DRIVER, "dummy", SDL_HINT_OVERRIDE);
    AuroraConfig config{};
    config.appName = "PSWaker installation error";
    config.userPath = "/data/pswaker";
    config.cachePath = "/data/pswaker/cache/" PSWAKER_BUILD_ID;
    config.resourcesPath = "/app0";
    config.desiredBackend = BACKEND_VULKAN;
    config.windowWidth = 1920; config.windowHeight = 1080;
    config.vsync = true; config.msaa = 1;
    config.logCallback = pswaker_aurora_log;
    const auto info = aurora_initialize(0, nullptr, &config);
    graphics = info.window != nullptr;
}
bool confirmScreen(const char* title, const char* text, bool allowExit) {
    bool released = false;
    for (;;) {
        screen(title, text, -1, "Retry", allowExit ? "Exit" : nullptr);
        pad state{};
        const bool connected = pad_player(0, &state);
        if (!connected) released = false;
        if (connected && !(state.held & (PAD_CROSS | PAD_CIRCLE))) released = true;
        if (released && connected && (state.held & PAD_CROSS)) return true;
        if (allowExit && released && connected && (state.held & PAD_CIRCLE)) return false;
        usleep(16000);
    }
}
bool storageProbe() {
    char path[] = "/data/pswaker/saves/.write-check-XXXXXX";
    const int fd = mkstemp(path);
    if (fd < 0) return false;
    bool good = write(fd, "PSWaker", 7) == 7;
    if (fsync(fd)) good = false;
    if (close(fd)) good = false;
    if (unlink(path)) good = false;
    return good;
}
void imageProgress(uint64_t done, uint64_t total) {
    static double next = 0;
    if (milliseconds() < next && done != total) return;
    next = milliseconds() + 250;
    say("CONTENT validation bytes=%llu/%llu ms=%.1f", (unsigned long long)done,
        (unsigned long long)total, milliseconds());
    screen("Checking installed game content", "Checking /app0/game.iso before starting the game.", float(done)/float(total));
}
void logDimensions() {
    aurora::gfx::synchronize();
    const auto& target = aurora::webgpu::g_frameBuffer.texture;
    const auto window = aurora::window::get_window_size();
    if (!target) pswaker_installation_error("The internal render target was not allocated; return this build's logs");
    say("DIMENSIONS allocated-internal=%ux%u output=%ux%u framebuffer=%ux%u ms=%.1f",
        target.GetWidth(), target.GetHeight(), window.width, window.height,
        window.fb_width, window.fb_height, milliseconds());
    if (target.GetWidth() != 1280 || target.GetHeight() != 720) {
        ++checkedErrors;
        pswaker_installation_error("The allocated internal render target is not 1280x720; report this build's logs");
    }
}
void logCache() {
    constexpr const char* cache = "/data/pswaker/cache/" PSWAKER_BUILD_ID;
    DIR* directory = opendir(cache);
    if (!directory) { say("ERROR cache directory unavailable errno=%d", errno); ++checkedErrors; return; }
    unsigned files = 0;
    while (const auto* entry = readdir(directory)) {
        if (entry->d_name[0] == '.') continue;
        char path[512];
        snprintf(path, sizeof path, "%s/%s", cache, entry->d_name);
        struct stat info{};
        if (stat(path, &info) || !S_ISREG(info.st_mode)) continue;
        FILE* input = fopen(path, "rb");
        char sha1[41]{};
        bool good = input && pswaker_hash_stream(input, info.st_size, sha1);
        if (input && fclose(input)) good = false;
        if (!good) ++checkedErrors;
        say("CACHE before-init name=%s bytes=%llu sha1=%s readable=%d", entry->d_name,
            (unsigned long long)info.st_size, sha1, good);
        ++files;
    }
    if (closedir(directory)) ++checkedErrors;
    say("CACHE identity=%s files-before-init=%u; owner labels cold/warm", PSWAKER_BUILD_ID, files);
}
}
void pswaker_stage(const char* name) {
    say("STAGE completed=%s ms=%.1f build=%s errors=%u", name, milliseconds(), PSWAKER_BUILD_ID, unsigned(checkedErrors));
    if (FILE* state = fopen("/data/pswaker/logs/last-stage.txt", "w")) {
        fprintf(state, "build=%s stage=%s elapsed_ms=%.1f checked_errors=%u\n", PSWAKER_BUILD_ID, name,
                milliseconds(), unsigned(checkedErrors));
        bool good = fflush(state) == 0;
        if (fsync(fileno(state))) good = false;
        if (fclose(state)) good = false;
        if (!good) { ++checkedErrors; say("ERROR writing last completed stage errno=%d", errno); }
    } else { ++checkedErrors; say("ERROR opening last-stage.txt errno=%d", errno); }
}
void pswaker_aurora_log(AuroraLogLevel level, const char* module, const char* message, unsigned length) {
    say("AURORA level=%d %s %.*s", int(level), module, int(length), message);
    if (level >= LOG_ERROR) ++checkedErrors;
    if (level == LOG_FATAL) { fflush(nullptr); abort(); }
}
void pswaker_graphics_ready() {
    JKRPcHostAllocScope hostAlloc;
    graphics = true;
    pswaker_stage("graphics-initialized");
    FILE* image = fopen("/app0/game.iso", "rb");
    char error[512];
    const bool valid = pswaker_validate_image(image, error, sizeof error, imageProgress);
    const bool closed = !image || fclose(image) == 0;
    if (!valid) pswaker_installation_error(error);
    if (!closed) pswaker_installation_error("Closing installed content failed");
    pswaker_stage("installed-image-validated");
    mkdir("/data/pswaker/saves", 0755);
    while (!storageProbe()) {
        ++checkedErrors;
        say("ERROR writable save storage check errno=%d", errno);
        if (!confirmScreen("Save storage unavailable", "Check free space and permissions for /data/pswaker/saves. Existing files will be preserved.", true)) pswaker_exit(2);
    }
    pswaker_stage("writable-storage-checked");
    VISetFrameBufferScale(1.5f);
    // Pump resize events and allocate a frame before querying actual GPU textures.
    screen("Preparing graphics", "Allocating the 1280x720 game render target.");
    screen("Preparing graphics", "Preparing shaders for this PS4 build.");
    logDimensions();
    const auto start = milliseconds();
    uint32_t previous = UINT32_MAX;
    for (;;) {
        const auto stats = pipelines();
        if (stats.created != previous) {
            previous = stats.created;
            say("SHADERS created=%u queued=%u ms=%.1f", stats.created, stats.queued, milliseconds());
        }
        char text[256];
        snprintf(text, sizeof text, "%u prepared; %u queued.\nNew shaders are compiled when first encountered. Gameplay shader stalls still count in later performance tests.", stats.created, stats.queued);
        screen("Shader preparation", text, stats.queued ? float(stats.created)/float(stats.created+stats.queued) : 1);
        if (!stats.queued) break;
        usleep(16000);
    }
    say("TIMING shader-preparation_ms=%.1f startup_to_preparation_complete_ms=%.1f", milliseconds()-start, milliseconds());
    pswaker_stage("known-shaders-prepared");
}
void pswaker_frame_boundary() {
    JKRPcHostAllocScope hostAlloc;
    static double next = 0;
    pswaker_enable_controls();
    while (pswaker_port_view().screen != PortScreen::Game) {
        if (pswaker_port_view().screen == PortScreen::Exit) pswaker_exit(0);
        screen("PSWaker - game paused", nullptr);
        pswaker_log_controls();
        usleep(16000);
    }
    pswaker_log_controls();
    if (milliseconds() >= next) {
        next = milliseconds()+5000;
        const auto stats = pipelines();
        say("HEARTBEAT ms=%.1f shaders-created=%u queued=%u checked-errors=%u", milliseconds(), stats.created,
            stats.queued, unsigned(checkedErrors));
        uint64_t frames = 0, squares = 0;
        COSAIGetOutputStats(&frames, &squares);
        say("AUDIO dma-frames=%llu sum-squares=%llu; audible output needs owner confirmation",
            (unsigned long long)frames, (unsigned long long)squares);
        pswaker_log_audio_output();
        pswaker_log_game_state();
    }
}
[[noreturn]] void pswaker_exit(int code) {
    JKRPcHostAllocScope hostAlloc;
    say("EXIT code=%d ms=%.1f checked-errors=%u", code, milliseconds(), unsigned(checkedErrors));
    quitting = true;
    if (graphics) {
        // Fatal paths may originate inside an SDK lock. Leave process cleanup to
        // the console there, without destroying a stream under its producer.
        if (code == 0) {
            pswaker_stage("shutdown-waiting-for-card");
            for (;;) {
                const auto deadline = milliseconds() + 30000;
                int status;
                while ((status = pswaker_card_shutdown_status()) == 0 && milliseconds() < deadline) {
                    screen("Finishing pending card work", "Waiting for an already requested card operation. Quitting does not save current gameplay.");
                    usleep(16000);
                }
                say("SHUTDOWN card-status=%d (0=busy 1=idle -1=last-store-failed)", status);
                if (status == 1) break;
                ++checkedErrors;
                if (!confirmScreen("Card work did not complete successfully",
                    "A previous save failed or card work is still pending. Retry waits again; Exit closes without claiming that progress was saved.", true)) {
                    code = 3;
                    break;
                }
            }
            pswaker_log_game_state();
            COSSdkRequestShutdown();
            const bool stopped = COSAIShutdownOutput() != 0;
            say("SHUTDOWN audio-producer-joined=%d", stopped);
            pswaker_log_audio_output();
            aurora::gfx::synchronize();
            say("SHUTDOWN gpu-synchronized=1");
            if (stopped) {
                aurora_shutdown();
                pswaker_log_audio_output(); // Includes the backend's final drain call.
                pswaker_stage(code == 0 ? "shutdown-complete" : "shutdown-with-card-error");
            }
            else { ++checkedErrors; say("ERROR audio producer could not be joined; retaining SDL until process exit"); }
        }
    }
    fflush(nullptr);
    catchReturnFromMain(code);
    for (;;) sleep(1);
}
[[noreturn]] void pswaker_installation_error(const char* reason) {
    JKRPcHostAllocScope hostAlloc;
    say("INSTALLATION ERROR: %s. Rebuild the complete package on the computer and reinstall. Saves/settings are preserved.", reason);
    ++checkedErrors;
    pswaker_stage("installation-error-stopped-before-gameplay");
    initializeErrorDisplay();
    if (graphics) {
        char text[1024];
        snprintf(text, sizeof text, "%s\n\nRebuild the complete package on the computer and reinstall. Existing saves/settings are preserved.", reason);
        bool released = false;
        for (;;) {
            screen("Installation error", text, -1, nullptr, "Exit");
            pad state{};
            if (pad_player(0, &state)) {
                if (!(state.held & PAD_CIRCLE)) released = true;
                if (released && (state.held & PAD_CIRCLE)) break;
            } else released = false;
            usleep(16000);
        }
    }
    pswaker_exit(14);
}
int main(int argc, char** argv) {
    mkdir("/data/pswaker", 0755);
    mkdir("/data/pswaker/logs", 0755);
    mkdir("/data/pswaker/cache", 0755);
    mkdir("/data/pswaker/cache/" PSWAKER_BUILD_ID, 0755);
    platform_init("PSWaker");
    say("BEGIN build=%s platform=PS4-Slim/9.00/GoldHEN-v2.4b18 owner-must-confirm; cache=/data/pswaker/cache/%s", PSWAKER_BUILD_ID, PSWAKER_BUILD_ID);
    if (FILE* manifest = fopen("/app0/complete-package.json", "r")) {
        char line[1024];
        while (fgets(line, sizeof line, manifest)) say("PACKAGE_MANIFEST %s", line);
        if (ferror(manifest)) { ++checkedErrors; say("ERROR reading package identity manifest"); }
        if (fclose(manifest)) { ++checkedErrors; say("ERROR closing package identity manifest"); }
    } else { ++checkedErrors; say("ERROR opening complete-package identity manifest errno=%d", errno); }
    logCache();
    setenv("COS_AUDIO", "on", 1);
    setenv("COS_UNCAPPED", "0", 1);
    setenv("COS_FPS60", "0", 1);
    setenv("COS_FPS60_TEST", "0", 1);
    setenv("COS_HD_TEXTURES", "0", 1);
    setenv("COS_DISC", "/app0/game.iso", 1);
    setenv("COS_SETTINGS", "/data/pswaker/settings.ini", 1);
    setenv("COS_RUN_DIR", "/data/pswaker/logs", 1);
    setenv("COS_CACHE_DIR", "/data/pswaker/cache/" PSWAKER_BUILD_ID, 1);
    setenv("COS_ASPECT", "16:9", 1);
    setenv("COS_FB_SCALE", "1.5", 1);
    setenv("COS_SYNC_PIPELINES", "1", 1);
    setenv("COS_PRECOMPILE", "off", 1); // preparation is reported explicitly above
    pswaker_stage("platform-initialized");
    pswaker_exit(aurora_main(argc, argv));
}
