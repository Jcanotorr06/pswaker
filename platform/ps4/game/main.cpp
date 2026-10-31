#include "game-platform.hpp"
#include "installed-content.hpp"
#include "controls.hpp"
#include "storage.hpp"
#include "frame-pacing.hpp"
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
#include "gfx/pipeline_cache.hpp"
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
extern "C" void ac_ps4_get_memory(uint64_t*, uint64_t*, uint64_t*);
extern "C" size_t pswaker_heap_used();
extern "C" int sceKernelAvailableFlexibleMemorySize(size_t*);
void pswaker_log_audio_output();
extern "C" uint64_t ps4_disc_busy_until_ns() { return 0; }
namespace {
const auto launch = std::chrono::steady_clock::now();
bool graphics = false;
bool quitting = false;
PortSettings settings;
bool settingsSaved = false;
std::string textError;
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
        const auto applied = pswaker_applied_controls();
        ImGui::TextUnformatted("Applied gameplay controls");
        for (const auto& line : applied.legend()) ImGui::TextUnformatted(line.c_str());
        for (const auto* line : applied.fixedGameplay) ImGui::TextUnformatted(line);
        if (*settings.controlsFeedback()) ImGui::TextWrapped("%s", settings.controlsFeedback());
        ImGui::TextUnformatted("Original GameCube prompts remain in the game.");
        ImGui::Separator();
        ImGui::TextUnformatted("Fixed port-menu controls");
        for (const auto* line : applied.fixedPort) ImGui::TextUnformatted(line);
        symbolLine(Symbol::Cross, "Continue / Return to settings");
        symbolLine(Symbol::Circle, "Back to settings (when opened from settings)");
    } else if (view.screen == PortScreen::Settings) {
        if (*settings.controlsFeedback()) ImGui::TextWrapped("%s", settings.controlsFeedback());
        ImGui::TextUnformatted("D-pad Up / Down: Choose");
        for (unsigned i = 0; i < portMenuItems.size(); ++i)
            ImGui::Text("%s %s", view.selection == i ? ">" : " ", portMenuItems[i].label);
        ImGui::Text("Port text size: %s", settings.largeText() ? "Large" : "Standard");
        ImGui::TextWrapped("%s", pswaker_perf_status());
        if (!textError.empty()) {
            ImGui::TextWrapped("Port text size could not be saved: %s", textError.c_str());
            ImGui::TextWrapped("Check free space/permissions, then select Change port text size to retry. Saving was not confirmed.");
        } else if (settingsSaved) ImGui::TextUnformatted("Port text size saved.");
        ImGui::Separator();
        symbolLine(Symbol::Cross, "Confirm"); symbolLine(Symbol::Circle, "Cancel / Resume game");
        ImGui::TextWrapped("The read check resumes gameplay, then pauses after 5 seconds. Hold movement, buttons and triggers during the check; explicitly resume afterward.");
    } else if (view.screen == PortScreen::Controls) {
        const auto applied = pswaker_applied_controls();
        ImGui::TextUnformatted("Controls: pending edits / applied layout");
        ImGui::TextUnformatted("D-pad Up / Down: Choose; Cross: Confirm");
        ImGui::TextUnformatted("Pending edits take effect only after Apply succeeds.");
        for (unsigned i = 0; i < gameActions.size(); ++i) {
            const auto action = gameActions[i];
            ImGui::Text("%s GameCube %s: pending %s | applied %s", view.controlsSelection == i ? ">" : " ",
                control_action_name(action), control_target_name(view.pendingControls.binding(action)),
                control_target_name(applied.config.binding(action)));
        }
        ImGui::Text("%s Invert camera X: pending %s | applied %s",
            view.controlsSelection == gameActions.size() ? ">" : " ",
            view.pendingControls.invertCameraX ? "On" : "Off", applied.config.invertCameraX ? "On" : "Off");
        ImGui::Text("%s Invert camera Y: pending %s | applied %s",
            view.controlsSelection == gameActions.size() + 1 ? ">" : " ",
            view.pendingControls.invertCameraY ? "On" : "Off", applied.config.invertCameraY ? "On" : "Off");
        ImGui::Text("%s Restore defaults...", view.controlsSelection == gameActions.size() + 2 ? ">" : " ");
        ImGui::Text("%s Apply", view.controlsSelection == gameActions.size() + 3 ? ">" : " ");
        ImGui::Text("%s Back to settings", view.controlsSelection == gameActions.size() + 4 ? ">" : " ");
        ImGui::TextUnformatted(view.controlsDirty ? "Unsaved changes" : "Pending values match the applied layout.");
        symbolLine(Symbol::Circle, "Back (unsaved edits require confirmation)");
    } else if (view.screen == PortScreen::Binding) {
        ImGui::Text("Choose a pending button for GameCube %s", control_action_name(gameActions[view.controlsSelection]));
        ImGui::TextUnformatted("D-pad Up / Down: Choose; occupied buttons swap actions.");
        for (unsigned i = 0; i < 9; ++i)
            ImGui::Text("%s %s", view.bindingSelection == i ? ">" : " ", control_target_name(static_cast<ControlTarget>(i)));
        symbolLine(Symbol::Cross, "Assign to pending layout");
        symbolLine(Symbol::Circle, "Keep the current pending binding");
    } else if (view.screen == PortScreen::RestoreControls) {
        ImGui::TextUnformatted("Restore default controls in pending edits?");
        ImGui::TextUnformatted("A = Cross; B = Circle; X = Square; Y = Triangle; Z = R1; Start = Options");
        ImGui::TextUnformatted("Both camera inversion switches will be Off. Other settings stay as they are.");
        ImGui::TextUnformatted("Review the pending defaults afterward, then Apply to save or Discard to keep the applied layout.");
        symbolLine(Symbol::Cross, "Restore pending defaults");
        symbolLine(Symbol::Circle, "Keep the current pending edits");
    } else if (view.screen == PortScreen::DiscardControls) {
        ImGui::TextUnformatted("Discard unsaved controls changes?");
        symbolLine(Symbol::Cross, "Discard and return to settings");
        symbolLine(Symbol::Circle, "Keep editing");
    } else if (view.screen == PortScreen::ApplyingControls) {
        ImGui::TextUnformatted("Applying controls...");
        ImGui::TextUnformatted("Saving the complete layout. Gameplay remains paused.");
    } else if (view.screen == PortScreen::ControlsFailed) {
        ImGui::TextUnformatted("Controls Apply was not confirmed.");
        ImGui::TextWrapped("%s", view.controlsError.c_str());
        ImGui::TextUnformatted("The previous applied layout remains active; pending edits are kept.");
        ImGui::TextWrapped("Check free space and permissions in /data/pswaker, then Retry. Disk completion may be uncertain; Retry saves the entire pending layout again.");
        symbolLine(Symbol::Cross, "Retry Apply");
        symbolLine(Symbol::Circle, "Discard edits and return to settings");
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
    ImGui::SetWindowFontScale(settings.largeText() ? 1.7f : 1.3f);
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
bool confirmScreen(const char* title, const char* text, bool allowExit, const char* confirm = "Retry") {
    bool released = false;
    for (;;) {
        screen(title, text, -1, confirm, allowExit ? "Exit" : nullptr);
        pad state{};
        const bool connected = pad_player(0, &state);
        if (!connected) released = false;
        if (connected && !(state.held & (PAD_CROSS | PAD_CIRCLE))) released = true;
        if (released && connected && (state.held & PAD_CROSS)) return true;
        if (allowExit && released && connected && (state.held & PAD_CIRCLE)) return false;
        usleep(16000);
    }
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
void pswaker_toggle_text_size() {
    settingsSaved = settings.setLargeText(!settings.largeText());
    textError = settings.error();
    say("SETTINGS saved=%d port-text=%s path=/data/pswaker/settings.ini error=%s",
        settingsSaved, settings.largeText() ? "large" : "standard", settings.error());
    if (!settingsSaved) ++checkedErrors;
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
    pswaker_perf_phase("content-validation");
    FILE* image = fopen("/app0/game.iso", "rb");
    char error[512];
    ImageRecord record{"/app0/complete-package.json", "/data/pswaker/installed-image-check.txt", PSWAKER_BUILD_ID};
    const auto check = pswaker_check_installed_image(image, record, error, sizeof error, imageProgress);
    const bool closed = !image || fclose(image) == 0;
    if (check == ImageCheck::Failed) pswaker_installation_error(error);
    if (!closed) pswaker_installation_error("Closing installed content failed");
    // Without a manifest every launch hashes; its read error is already counted above.
    if (check == ImageCheck::FullUnrecorded && *record.identity) {
        ++checkedErrors;
        say("ERROR recording full image check path=%s; the next launch hashes again", record.path);
    }
    say("CONTENT check=%s identity='%s' ms=%.1f", check == ImageCheck::MatchedRecord ? "recorded-full-check" :
        check == ImageCheck::FullRecorded ? "full-recorded" : "full-unrecorded", record.identity, milliseconds());
    pswaker_stage("installed-image-validated");
    pswaker_perf_phase("storage-check");
    while (!settings.check()) {
        ++checkedErrors;
        say("ERROR writable profile storage check: %s", settings.error());
        char message[1024];
        snprintf(message, sizeof message, "%s\n\nCheck free space, permissions and the indicated path under /data/pswaker. Existing saves/settings are preserved. Repair the problem, then Retry; or Exit.", settings.error());
        if (!confirmScreen("Save/settings storage unavailable", message, true)) pswaker_exit(2);
    }
    if (!pswaker_publish_controls(settings.controls()))
        pswaker_installation_error("Could not publish the complete controls configuration.");
    if (*settings.controlsFeedback()) say("CONTROLS %s", settings.controlsFeedback());
    say("STORAGE checked shared-profile=/data/pswaker settings=/data/pswaker/settings.ini port-text=%s GCI-A='/data/pswaker/saves/USA/Card A' GCI-B='/data/pswaker/saves/USA/Card B' signed-in-user=independent", settings.largeText() ? "large" : "standard");
    pswaker_stage("writable-storage-checked");
    for (const char* channel : {"A", "B"}) {
        SaveFile save(std::string("/data/pswaker/saves/USA/Card ") + channel + "/01-GZLE-gczelda.gci");
        while (!save.check()) {
            ++checkedErrors;
            const bool backup = save.canRestore();
            say("RECOVERY blocked=%s valid-backup=%d choice=pending", save.error(), backup);
            char message[1400];
            snprintf(message, sizeof message, "%s\n\n%s", save.error(), backup ?
                "A valid previous save backup exists. Cross explicitly restores that older progress; affected files are retained as evidence. Circle declines and exits without changing progress." :
                "No valid backup is available. Exit and copy this card directory to the computer for recovery. Check storage/permissions and Retry after repair. Do not delete or initialize your progress.");
            if (!confirmScreen("Save recovery required", message, true, backup ? "Restore previous save" : "Retry")) {
                say("RECOVERY choice=decline-exit channel=%s affected-data=preserved", channel);
                pswaker_exit(3);
            }
            if (backup) {
                const bool restored = save.restore();
                say("RECOVERY choice=restore channel=%s confirmed=%d error=%s", channel, restored, save.error());
                if (!restored && !confirmScreen("Restore was not confirmed", save.error(), true)) pswaker_exit(3);
            }
        }
        const auto testMode = save.testMode();
        if (!testMode.empty()) {
            say("STORAGE TEST startup channel=%s mode=%s awaiting-explicit-choice", channel, testMode.c_str());
            if (!confirmScreen("Controlled storage test is enabled",
                "This card has a .test marker. fail-write deliberately fails saves; hold-publish delays completion by 20 seconds. Use only disposable test progress. Exit and remove the marker to return to normal play.", true, "Continue controlled test")) pswaker_exit(3);
        }
    }
    pswaker_stage("save-recovery-checked");
    VISetFrameBufferScale(1.5f);
    // Pump resize events and allocate a frame before querying actual GPU textures.
    screen("Preparing graphics", "Allocating the 1280x720 game render target.");
    screen("Preparing graphics", "Preparing shaders for this PS4 build.");
    logDimensions();
    const auto start = milliseconds();
    pswaker_perf_phase("shader-preparation");
    uint32_t previous = UINT32_MAX;
    for (;;) {
        // Drain earlier frame work before testing the renderer's preparation
        // contract. Its pending set includes creation already inside the driver.
        aurora::gfx::synchronize();
        const auto status = aurora::gfx::pipeline_preparation_status();
        if (status.error) pswaker_installation_error(status.error);
        if (status.ready != previous) {
            previous = status.ready;
            say("SHADERS configurations-ready=%u total=%u pending=%u complete=%d ms=%.1f",
                status.ready, status.total, status.pending, status.complete, milliseconds());
        }
        char text[256];
        snprintf(text, sizeof text, "%u of %u shader configurations prepared.\nConfigurations not included in this package compile when first encountered.",
                 status.ready, status.total);
        screen("Shader preparation", text, status.complete ? 1.f :
               status.total ? float(status.ready)/float(status.total) : 0.f);
        if (status.complete) {
            aurora::gfx::synchronize();
            const auto finalStatus = aurora::gfx::pipeline_preparation_status();
            if (finalStatus.error) pswaker_installation_error(finalStatus.error);
            if (!finalStatus.complete || !aurora::gfx::finish_pipeline_preparation()) continue;
            // Include seed loading and compilation that overlapped content and
            // storage checks, while retaining the final screen drain separately.
            say("TIMING shader-preparation_ms=%.1f shader-final-drain_ms=%.1f startup_to_preparation_complete_ms=%.1f preparation_start_ns=%llu preparation_complete_ns=%llu",
                double(finalStatus.finishedNs-finalStatus.startedNs)/1e6, milliseconds()-start, milliseconds(),
                (unsigned long long)finalStatus.startedNs, (unsigned long long)finalStatus.finishedNs);
            break;
        }
        usleep(16000);
    }
    pswaker_stage("known-shaders-prepared");
    pswaker_perf_phase("loading");
}
void pswaker_frame_boundary() {
    JKRPcHostAllocScope hostAlloc;
    static double next = 0;
    pswaker_enable_controls(settings);
    // The worker records failure only after the transaction finishes. Stop at
    // the next frame boundary so affected progress cannot be overwritten.
    if (pswaker_card_shutdown_status() < 0) pswaker_exit(0);
    while (pswaker_port_view().screen != PortScreen::Game) {
        pswaker_perf_pause();
        if (pswaker_port_view().screen == PortScreen::Exit) pswaker_exit(0);
        screen("PSWaker - game paused", nullptr);
        pswaker_log_controls();
        usleep(16000);
    }
    pswaker_log_controls();
    if (milliseconds() >= next) {
        const auto diagnosticStart = pswaker_perf_now();
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
        uint64_t garlic = 0, onion = 0, buffers = 0;
        ac_ps4_get_memory(&garlic, &onion, &buffers);
        size_t flexible = 0;
        const int result = sceKernelAvailableFlexibleMemorySize(&flexible);
        say("RESOURCE ms=%.1f garlic=%llu onion=%llu buffers=%llu main-mspace-allocated=%zu flexible-available=%zu query-result=%d",
            milliseconds(), (unsigned long long)garlic, (unsigned long long)onion,
            (unsigned long long)buffers, pswaker_heap_used(), flexible, result);
        pswaker_perf_diagnostic(PswakerDiagnostic::Heartbeat, diagnosticStart);
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
                bool reportedPending = false;
                while ((status = pswaker_card_shutdown_status()) == 0 && milliseconds() < deadline) {
                    if (!reportedPending) { say("SHUTDOWN card-status=0 pending; waiting without requesting a save"); reportedPending = true; }
                    screen("Finishing pending card work", "Waiting for an already requested card operation. Quitting does not save current gameplay.");
                    usleep(16000);
                }
                say("SHUTDOWN card-status=%d (0=busy 1=idle -1=last-store-failed)", status);
                if (status == 1) break;
                ++checkedErrors;
                if (status == 0) {
                    confirmScreen("Card work is still pending",
                        "Quit must wait for the requested save. Retry continues waiting; current gameplay is not automatically saved.", false);
                    continue;
                }
                if (!confirmScreen("Card work did not complete successfully",
                    "The requested save failed. Previous valid save/backup and affected data are retained. Exit, repair storage and relaunch for recovery. Retry checks completion again; no new save is requested.", true)) {
                    code = 3;
                    break;
                }
            }
            pswaker_stage("shutdown-card-finished");
            pswaker_log_game_state();
            pswaker_stage("shutdown-requesting-sdk-stop");
            COSSdkRequestShutdown();
            pswaker_stage("shutdown-sdk-stop-requested");
            const bool stopped = COSAIShutdownOutput() != 0;
            say("SHUTDOWN audio-producer-joined=%d", stopped);
            pswaker_log_audio_output();
            aurora::gfx::synchronize();
            say("SHUTDOWN gpu-synchronized=1");
            pswaker_perf_shutdown();
            if (stopped) {
                aurora_shutdown();
                pswaker_log_audio_output(); // Includes the backend's final drain call.
                pswaker_stage(code == 0 ? "shutdown-complete" : "shutdown-with-card-error");
            }
            else { ++checkedErrors; say("ERROR audio producer could not be joined; retaining SDL until process exit"); }
        }
    }
    fflush(nullptr);
    pswaker_perf_shutdown();
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
    pswaker_perf_initialize(PSWAKER_BUILD_ID);
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
