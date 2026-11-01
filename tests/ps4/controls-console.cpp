// Only the external console service boundary is simulated. No game data or GPU.
#include "controls.hpp"
#include "prompts.hpp"
#include "message-prompts.hpp"
#include "storage.hpp"
#include "frame-pacing.hpp"
#include "native/platform.h"
#include "pc/pc_controls.h"
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <filesystem>
#include <thread>
#include <time.h>

namespace {
uint32_t buttons = 0;
uint8_t lx = 128, ly = 128, rx = 128, ry = 128, lt = 0, rt = 0;
bool connected = true;
bool fail = false;
bool failSync = false, failClose = false, failRename = false;
int syncCountdown = -1;
unsigned textChanges = 0;
PortSettings* settings = nullptr;
double clockValue = 1000;
PADStatus gamepads[PAD_CHANMAX];

struct RetainedPrompt {
    bool ready = true;
    PromptResult rendered;
};
bool rebuildPrompt(void* context, const AppliedControls& applied) {
    auto& picture = *static_cast<RetainedPrompt*>(context);
    if (!picture.ready) return false;
    picture.rendered = resolve_ps4_prompt({GameAction::A}, applied);
    return true;
}

// A retained message picture, as the game's J2DPicture hook sees it.
struct MessagePicture { const void* image = nullptr; };
void showMessagePicture(void* picture, void*, const void* image, const void*) {
    static_cast<MessagePicture*>(picture)->image = image;
}

void sample(uint32_t held = 0) {
    buttons = held;
    clockValue += .02;
    pswaker_poll_controls();
    pswaker_read_gamepad(gamepads);
}
void neutralGame() {
    for (const auto& p : gamepads) {
        assert(p.button == 0 && p.extButton == 0);
        assert(p.stickX == 0 && p.stickY == 0 && p.substickX == 0 && p.substickY == 0);
        assert(p.triggerLeft == 0 && p.triggerRight == 0 && p.analogA == 0 && p.analogB == 0);
    }
}
void start() {
    assert(pad_open());
    pswaker_enable_controls(*settings);
    sample(PAD_CROSS); // Held during first launch must not confirm.
    assert(pswaker_port_view().screen == PortScreen::Legend);
    neutralGame();
    sample(); sample(PAD_CROSS);
    neutralGame(); // Confirmation is consumed, even before release.
    sample();
    assert(pswaker_port_view().screen == PortScreen::Game);
    assert(gamepads[0].button == 0);
}
void tap(uint32_t button) {
    sample(button); neutralGame(); sample(); neutralGame();
}
void openEditor() {
    tap(PAD_TOUCH_PAD);
    for (unsigned i = 0; portMenuItems[pswaker_port_view().selection].action != PortAction::EditControls; ++i) {
        assert(i < portMenuItems.size());
        tap(PAD_DOWN);
    }
    tap(PAD_CROSS);
    assert(pswaker_port_view().screen == PortScreen::Controls);
}
void editorRow(unsigned row) {
    for (unsigned i = 0; pswaker_port_view().controlsSelection != row; ++i) {
        assert(i < 11);
        tap(PAD_DOWN);
    }
}
void assignButton(unsigned row, unsigned target) {
    editorRow(row);
    tap(PAD_CROSS);
    assert(pswaker_port_view().screen == PortScreen::Binding);
    for (unsigned i = 0; pswaker_port_view().bindingSelection != target; ++i) {
        assert(i < 9);
        tap(PAD_DOWN);
    }
    tap(PAD_CROSS);
    assert(pswaker_port_view().screen == PortScreen::Controls);
    assert(pswaker_port_view().pendingControls.valid());
}
std::string readProfile(const std::string& path) {
    std::ifstream file(path);
    return {std::istreambuf_iterator<char>(file), {}};
}
}
// The pinned control options only use this harness logger for environment feedback.
namespace pc { void writef(int, const char*, ...) {} }
extern "C" {
int __real_fsync(int);
int __wrap_fsync(int fd) {
    if (failSync || syncCountdown == 0) { errno = EIO; return -1; }
    if (syncCountdown > 0) --syncCountdown;
    return __real_fsync(fd);
}
int __real_close(int);
int __wrap_close(int fd) {
    const int result = __real_close(fd);
    if (failClose) { errno = EIO; return -1; }
    return result;
}
int __real_rename(const char*, const char*);
int __wrap_rename(const char* from, const char* to) {
    if (failRename) { errno = EIO; return -1; }
    return __real_rename(from, to);
}
int clock_gettime(clockid_t, struct timespec* output) noexcept {
    output->tv_sec = static_cast<time_t>(clockValue);
    output->tv_nsec = static_cast<long>((clockValue - output->tv_sec) * 1e9);
    return 0;
}
int sceSysmoduleLoadModuleInternal(uint32_t) { return 0; }
int sceSystemServiceHideSplashScreen() { return 0; }
int sceSystemServiceLoadExec(const char*, char* const*) { return 0; }
int sceUserServiceInitialize(const void*) { return 0; }
int sceUserServiceGetInitialUser(int32_t* user) { *user = 1; return 0; }
int sceUserServiceGetLoginUserIdList(int32_t* users) {
    users[0] = 1; users[1] = users[2] = users[3] = -1; return 0;
}
int scePadInit() { return 0; }
int scePadOpen(int32_t, int32_t, int32_t, const void*) { return 1; }
int scePadGetHandle(int32_t, uint32_t, uint32_t) { return 1; }
int scePadClose(int32_t) { return 0; }
int scePadSetVibration(int32_t, const void*) { return 0; }
int scePadSetLightBar(int32_t, const void*) { return 0; }
int sceKernelUsleep(unsigned int) { return 0; }
int sceKernelDebugOutText(int, const char*) { return 0; }
int scePadReadState(int32_t, void* output) {
    // OrbisPadData wire offsets, independent of the production struct.
    auto* bytes = static_cast<uint8_t*>(output);
    std::memset(bytes, 0, 120);
    std::memcpy(bytes, &buttons, 4);
    bytes[4] = lx; bytes[5] = ly; bytes[6] = rx; bytes[7] = ry;
    bytes[8] = lt; bytes[9] = rt; bytes[0x4c] = connected;
    return fail ? -1 : 0;
}
}
void pswaker_toggle_text_size() {
    ++textChanges;
    assert(settings && settings->setLargeText(!settings->largeText()));
}
// Performance actions are outside the existing controls scenarios.
void pswaker_perf_arm(const char*) {}
void pswaker_perf_phase(const char*) {}
extern "C" uint64_t pswaker_perf_now() { return 0; }
void pswaker_perf_diagnostic(PswakerDiagnostic, uint64_t) {}
void pswaker_report_prompt_coverage(const char* surface, unsigned item, const char* reason) {
    std::fprintf(stderr, "unexpected unresolved %s %u: %s\n", surface, item, reason);
    std::abort();
}
int main(int argc, char** argv) {
    assert(argc == 3);
    PortSettings initialProfile(argv[2]);
    settings = &initialProfile;
    if (std::strncmp(argv[1], "prompt-", 7) == 0) {
        const std::string scenario = argv[1] + 7;
        assert(settings->check() && pswaker_publish_controls(settings->controls()));
        RetainedPrompt dialog, hud;
        assert(pswaker_register_prompt_adapter(&dialog, rebuildPrompt));
        assert(pswaker_register_prompt_adapter(&hud, rebuildPrompt));
        assert(pswaker_register_prompt_adapter(nullptr, pswaker_refresh_message_prompts));
        start();
        const auto previous = pswaker_applied_controls();
        // A dialog showing the A picture stays open across the whole Apply flow.
        MessagePicture openDialog;
        assert(pswaker_message_picture_set(&openDialog, nullptr, 0x00, 0, showMessagePicture));
        const auto* cross = message_prompt_texture({Ps4Icon::Cross}, false);
        const auto* r3 = message_prompt_texture({Ps4Icon::R3}, false);
        assert(openDialog.image == cross);
        assert(dialog.rendered.name == "Cross" && dialog.rendered.generation == previous.generation);
        assert(hud.rendered.generation == previous.generation);
        openEditor(); assignButton(0, static_cast<unsigned>(ControlTarget::R3));
        assert(resolve_ps4_prompt({GameAction::A}, pswaker_applied_controls()).name == "Cross");
        assert(dialog.rendered.generation == previous.generation);
        if (scenario == "discard") {
            tap(PAD_CIRCLE); tap(PAD_CROSS);
        } else {
            failRename = scenario == "failure";
            syncCountdown = scenario == "uncertain" ? 1 : -1;
            editorRow(9); tap(PAD_CROSS); sample(); neutralGame(); sample();
            if (scenario == "failure" || scenario == "uncertain") {
                assert(pswaker_port_view().screen == PortScreen::ControlsFailed);
                assert(pswaker_applied_controls().generation == previous.generation);
                assert(dialog.rendered.generation == previous.generation);
                failRename = false; syncCountdown = -1;
                tap(PAD_CIRCLE);
            } else {
                assert(pswaker_port_view().screen == PortScreen::Controls);
                assert(pswaker_applied_controls().generation == previous.generation + 1);
                assert(pswaker_applied_controls().legend()[0] == "GameCube A = R3");
                tap(PAD_CIRCLE);
            }
        }
        assert(pswaker_port_view().screen == PortScreen::Settings);
        const auto published = pswaker_applied_controls();
        // Two retained surfaces join the real release gate. One needs another
        // frame to rebuild; successful peers must not release gameplay early.
        hud.ready = scenario == "discard" || scenario == "failure" || scenario == "uncertain";
        sample(PAD_CIRCLE); sample(PAD_CIRCLE); neutralGame();
        assert(pswaker_port_view().releasing);
        sample();
        if (!hud.ready) {
            neutralGame();
            assert(pswaker_port_view().screen == PortScreen::Settings && pswaker_port_view().releasing);
            assert(pswaker_port_view().refreshingPrompts);
            assert(dialog.rendered.name == "R3" && dialog.rendered.generation == published.generation);
            assert(hud.rendered.name == "Cross" && hud.rendered.generation == previous.generation);
            assert(openDialog.image == r3); // Rebuilt before gameplay can resume.
            // Disconnect during refresh still requires a new fixed confirmation.
            connected = false; sample(PAD_R3); neutralGame();
            assert(pswaker_port_view().screen == PortScreen::InputLost);
            connected = true; hud.ready = true;
            lx = 255; lt = rt = 255; sample(PAD_CROSS | PAD_R3); neutralGame();
            sample(); neutralGame();
            lx = 128; lt = rt = 0; sample(); neutralGame();
            assert(pswaker_port_view().screen == PortScreen::InputLost);
            sample(PAD_CROSS); neutralGame();
            sample(PAD_R3); neutralGame();
            sample();
        }
        assert(pswaker_port_view().screen == PortScreen::Game);
        assert(gamepads[0].button == 0);
        assert(dialog.rendered.generation == published.generation && hud.rendered.generation == published.generation);
        const auto expected = hud.ready && scenario == "apply" ? "R3" : "Cross";
        assert(dialog.rendered.name == expected && hud.rendered.name == expected);
        assert(resolve_ps4_prompt({GameAction::A}, published).name == expected);
        assert(openDialog.image == (hud.ready && scenario == "apply" ? r3 : cross));
        return 0;
    }
    if (std::strncmp(argv[1], "inversion-apply-", 16) == 0) {
        const std::string scenario = argv[1] + 16;
        const auto split = scenario.find('-');
        const auto axes = scenario.substr(0, split);
        const auto fault = split == std::string::npos ? "" : scenario.substr(split + 1);
        const bool x = axes == "x" || axes == "both";
        const bool y = axes == "y" || axes == "both";
        // Environment defaults must not override the port's authoritative profile.
        setenv("COS_CAMERA_INVERT_X", "1", 1);
        setenv("COS_CAMERA_INVERT_Y", "1", 1);
        assert(settings->check() && pswaker_publish_controls(settings->controls()));
        const auto applied = pswaker_applied_controls();
        assert(!pc_camera_invert_x() && !pc_camera_invert_y());
        start(); openEditor();
        assignButton(0, static_cast<unsigned>(ControlTarget::L3));
        if (x) { editorRow(6); tap(PAD_CROSS); }
        if (y) { editorRow(7); tap(PAD_CROSS); }
        const auto pending = pswaker_port_view().pendingControls;
        assert(pending.invertCameraX == x && pending.invertCameraY == y);
        assert(!pc_camera_invert_x() && !pc_camera_invert_y());
        assert(pswaker_applied_controls().generation == applied.generation);
        if (fault == "discard") {
            tap(PAD_CIRCLE);
            assert(pswaker_port_view().screen == PortScreen::DiscardControls);
            tap(PAD_CROSS);
            assert(pswaker_port_view().pendingControls == applied.config);
            assert(pswaker_applied_controls().generation == applied.generation);
            assert(!pc_camera_invert_x() && !pc_camera_invert_y());
            assert(!std::filesystem::exists(std::string(argv[2]) + "/settings.ini"));
            return 0;
        }
        failSync = fault == "sync";
        failClose = fault == "close";
        failRename = fault == "rename" || fault == "failed-discard";
        syncCountdown = fault.starts_with("uncertain") ? 2 : -1;
        editorRow(9); tap(PAD_CROSS);
        assert(pswaker_port_view().screen == PortScreen::ApplyingControls);
        assert(!pc_camera_invert_x() && !pc_camera_invert_y());
        sample(); neutralGame(); sample();
        if (!fault.empty()) {
            assert(pswaker_port_view().screen == PortScreen::ControlsFailed);
            assert(!pswaker_port_view().controlsError.empty());
            assert(pswaker_port_view().pendingControls == pending);
            assert(pswaker_applied_controls().config == applied.config);
            assert(pswaker_applied_controls().generation == applied.generation);
            assert(!pc_camera_invert_x() && !pc_camera_invert_y());
            failSync = failClose = failRename = false; syncCountdown = -1;
            if (fault.ends_with("discard")) {
                tap(PAD_CIRCLE);
                assert(pswaker_port_view().screen == PortScreen::Settings);
                assert(pswaker_port_view().pendingControls == applied.config);
                assert(pswaker_applied_controls().generation == applied.generation);
                assert(!pc_camera_invert_x() && !pc_camera_invert_y());
                return 0;
            }
            tap(PAD_CROSS); sample(); neutralGame(); sample();
        }
        assert(pswaker_applied_controls().config == pending);
        assert(pswaker_applied_controls().generation == applied.generation + 1);
        assert(bool(pc_camera_invert_x()) == x && bool(pc_camera_invert_y()) == y);
        PortSettings reloaded(argv[2]);
        assert(reloaded.check() && reloaded.controls() == pending);
        assert(pswaker_publish_controls(ControlsConfig::defaults()));
        assert(!pc_camera_invert_x() && !pc_camera_invert_y());
        assert(pswaker_publish_controls(reloaded.controls()));
        assert(bool(pc_camera_invert_x()) == x && bool(pc_camera_invert_y()) == y);
        tap(PAD_CIRCLE); tap(PAD_CIRCLE);
        sample(PAD_L3); assert(gamepads[0].button == PAD_BUTTON_A);
        // Neither stick is globally negated, and fixed D-pad/trigger input survives.
        lx = rx = 255; ly = ry = 0; lt = 229; rt = 230;
        sample(PAD_UP);
        assert(gamepads[0].stickX == 127 && gamepads[0].stickY == 127);
        assert(gamepads[0].substickX == 127 && gamepads[0].substickY == 127);
        assert(gamepads[0].button == (PAD_BUTTON_UP | PAD_TRIGGER_R));
        assert(gamepads[0].triggerLeft == 229 && gamepads[0].triggerRight == 230);
        return 0;
    }
    if (std::strcmp(argv[1], "inversion-pending") == 0) {
        assert(settings->check() && pswaker_publish_controls(settings->controls()));
        const auto applied = pswaker_applied_controls();
        assert(!applied.config.invertCameraX && !applied.config.invertCameraY);
        start(); openEditor();
        // Walk all four combinations; holding confirm must toggle only once.
        for (const auto row : {6u, 7u, 6u, 7u}) {
            const auto before = pswaker_port_view().pendingControls;
            editorRow(row);
            sample(PAD_CROSS); sample(PAD_CROSS); neutralGame(); sample();
            assert(pswaker_port_view().screen == PortScreen::Controls);
            const auto pending = pswaker_port_view().pendingControls;
            assert(pending.invertCameraX == (row == 6 ? !before.invertCameraX : before.invertCameraX));
            assert(pending.invertCameraY == (row == 7 ? !before.invertCameraY : before.invertCameraY));
            assert(pswaker_applied_controls().config == applied.config);
            assert(pswaker_applied_controls().generation == applied.generation);
            assert(!std::filesystem::exists(std::string(argv[2]) + "/settings.ini"));
        }
        assert(!pswaker_port_view().controlsDirty);
        return 0;
    }
    if (std::strncmp(argv[1], "restore-", 8) == 0) {
        const std::string scenario = argv[1] + 8;
        const std::string prefix = "# owner settings\nPSWAKER_LARGE_TEXT=0\nOWNER_SETTING=keep\n";
        const std::string suffix = "[audio]\nvolume=70\n[dev]\nCOS_FPS60=1\n";
        const std::string previous = prefix + "[controls]\nversion=1\n"
            "A=L3\nB=R3\nX=L1\nY=Options\nZ=Cross\nStart=Circle\n"
            "invert_camera_x=1\ninvert_camera_y=1\n" + suffix;
        const std::string savedDefaults = prefix + "[audio]\nvolume=70\n[controls]\nversion=1\n"
            "A=Cross\nB=Circle\nX=Square\nY=Triangle\nZ=R1\nStart=Options\n"
            "invert_camera_x=0\ninvert_camera_y=0\n[dev]\nCOS_FPS60=1\n";
        const ControlsConfig defaults{{ControlTarget::Cross, ControlTarget::Circle, ControlTarget::Square,
            ControlTarget::Triangle, ControlTarget::R1, ControlTarget::Options}, false, false};
        const auto ini = std::string(argv[2]) + "/settings.ini";
        std::ofstream(ini) << previous;
        assert(settings->check() && !settings->largeText() && pswaker_publish_controls(settings->controls()));
        const auto applied = pswaker_applied_controls();
        const auto unchanged = [&] {
            assert(pswaker_applied_controls().config == applied.config);
            assert(pswaker_applied_controls().generation == applied.generation);
            assert(pswaker_applied_controls().legend() == applied.legend());
            assert(!settings->largeText() && textChanges == 0);
        };
        start(); openEditor(); assignButton(0, 7);
        const auto pending = pswaker_port_view().pendingControls;
        editorRow(8);
        // Holding confirm opens only the prompt, never also confirms the reset.
        sample(PAD_CROSS); sample(PAD_CROSS); neutralGame();
        assert(pswaker_port_view().pendingControls == pending);
        sample();
        assert(pswaker_port_view().screen == PortScreen::RestoreControls);
        unchanged();
        assert(readProfile(ini) == previous);
        if (scenario == "loss") {
            lx = 255; rx = 0; lt = rt = 255;
            connected = false; sample(PAD_CROSS | PAD_L3); neutralGame();
            assert(pswaker_port_view().screen == PortScreen::InputLost);
            connected = true; sample(PAD_CROSS); neutralGame();
            lx = rx = 128; lt = rt = 0; sample();
            assert(pswaker_port_view().screen == PortScreen::InputLost);
            tap(PAD_CROSS);
            assert(pswaker_port_view().screen == PortScreen::RestoreControls);
            assert(pswaker_port_view().pendingControls == pending);
            unchanged();
            assert(readProfile(ini) == previous);
        }
        if (scenario == "cancel") {
            tap(PAD_CIRCLE);
            assert(pswaker_port_view().screen == PortScreen::Controls);
            assert(pswaker_port_view().pendingControls == pending);
            assert(pswaker_port_view().controlsDirty);
            unchanged();
            assert(readProfile(ini) == previous);
            return 0;
        }
        sample(PAD_CROSS); neutralGame(); sample(PAD_CROSS); neutralGame();
        assert(pswaker_port_view().pendingControls == defaults);
        sample();
        assert(pswaker_port_view().screen == PortScreen::Controls);
        assert(pswaker_port_view().pendingControls == defaults);
        unchanged();
        assert(readProfile(ini) == previous);
        if (scenario == "discard" || scenario == "loss") {
            tap(PAD_CIRCLE);
            assert(pswaker_port_view().screen == PortScreen::DiscardControls);
            tap(PAD_CROSS);
            assert(pswaker_port_view().screen == PortScreen::Settings);
            assert(pswaker_port_view().pendingControls == applied.config);
            unchanged();
            assert(readProfile(ini) == previous);
            sample(PAD_CIRCLE); sample(PAD_L3 | PAD_CROSS); neutralGame();
            assert(pswaker_port_view().releasing);
            sample();
            assert(pswaker_port_view().screen == PortScreen::Game);
            sample(PAD_L3); assert(gamepads[0].button == 0x100);
            sample(PAD_CROSS); assert(gamepads[0].button == 0x10);
            return 0;
        }
        if (scenario == "apply" || scenario.starts_with("fail-")) {
            const auto fault = scenario.starts_with("fail-") ? scenario.substr(5) : "";
            const bool uncertain = fault.starts_with("uncertain");
            failSync = fault == "sync";
            failClose = fault == "close";
            failRename = fault == "rename" || fault == "discard";
            syncCountdown = uncertain ? 2 : -1;
            editorRow(9); tap(PAD_CROSS);
            assert(pswaker_port_view().screen == PortScreen::ApplyingControls);
            unchanged();
            sample(); neutralGame();
            if (!fault.empty()) {
                assert(pswaker_port_view().screen == PortScreen::ControlsFailed);
                assert(!pswaker_port_view().controlsError.empty());
                assert(pswaker_port_view().pendingControls == defaults);
                unchanged();
                assert(readProfile(ini) == (uncertain ? savedDefaults : previous));
                sample(PAD_CROSS); sample(PAD_CROSS); neutralGame();
                assert(pswaker_port_view().screen == PortScreen::ControlsFailed);
                failSync = failClose = failRename = false;
                syncCountdown = -1;
                sample();
                if (fault.ends_with("discard")) {
                    tap(PAD_CIRCLE);
                    assert(pswaker_port_view().screen == PortScreen::Settings);
                    assert(pswaker_port_view().pendingControls == applied.config);
                    unchanged();
                    assert(readProfile(ini) == (uncertain ? savedDefaults : previous));
                    tap(PAD_CIRCLE);
                    sample(PAD_L3); assert(gamepads[0].button == 0x100);
                    return 0;
                }
                // Uncertain completion may already have replaced the file. Retry must
                // save the whole pending reset even if disk contents change afterward.
                if (uncertain) std::ofstream(ini) << previous;
                tap(PAD_CROSS);
                assert(pswaker_port_view().screen == PortScreen::ApplyingControls);
                sample(); neutralGame();
            }
            sample();
            assert(pswaker_port_view().screen == PortScreen::Controls);
            assert(!pswaker_port_view().controlsDirty && pswaker_port_view().controlsError.empty());
            const auto reset = pswaker_applied_controls();
            assert(reset.config == defaults && reset.generation == applied.generation + 1);
            const std::array<std::string, 8> legend{
                "GameCube A = Cross", "GameCube B = Circle", "GameCube X = Square",
                "GameCube Y = Triangle", "GameCube Z = R1", "GameCube Start = Options",
                "Saved camera inversion X: Off", "Saved camera inversion Y: Off"};
            assert(reset.legend() == legend);
            assert(readProfile(ini) == savedDefaults);
            PortSettings disk(argv[2]);
            assert(disk.check() && disk.controls() == defaults && !disk.largeText());
            assert(!settings->largeText() && textChanges == 0);
            tap(PAD_CIRCLE);
            sample(PAD_CIRCLE); sample(PAD_CROSS); neutralGame(); sample();
            assert(pswaker_port_view().screen == PortScreen::Game);
            const uint32_t physical[] = {PAD_CROSS, PAD_CIRCLE, PAD_SQUARE, PAD_TRIANGLE, PAD_R1, PAD_OPTIONS};
            const uint16_t actions[] = {0x100, 0x200, 0x400, 0x800, 0x10, 0x1000};
            for (unsigned i = 0; i < 6; ++i) {
                sample(physical[i]); assert(gamepads[0].button == actions[i]); sample();
            }
            return 0;
        }
        assert(false && "unknown restore scenario");
    }
    if (std::strcmp(argv[1], "editor-all-targets") == 0) {
        assert(settings->check());
        start(); openEditor();
        const uint32_t physical[] = {0x4000, 0x2000, 0x8000, 0x1000, 0x400, 0x800, 2, 4, 8};
        const uint16_t actions[] = {0x100, 0x200, 0x400, 0x800, 0x10, 0x1000};
        uint64_t generation = pswaker_applied_controls().generation;
        for (unsigned action = 0; action < 6; ++action) {
            for (unsigned target = 0; target < 9; ++target) {
                assignButton(action, target);
                const auto pending = pswaker_port_view().pendingControls;
                assert(static_cast<unsigned>(pending.binding(gameActions[action])) == target);
                assert(pswaker_applied_controls().generation == generation);
                editorRow(9); tap(PAD_CROSS); sample(); sample();
                assert(pswaker_applied_controls().generation == ++generation);
                assert(pswaker_applied_controls().config == pending);
                tap(PAD_CIRCLE); tap(PAD_CIRCLE);
                assert(pswaker_port_view().screen == PortScreen::Game);
                sample(physical[target]);
                assert(gamepads[0].button == actions[action]);
                sample(); openEditor();
            }
        }
        return 0;
    }
    if (std::strcmp(argv[1], "editor-loss") == 0) {
        assert(settings->check());
        start(); openEditor(); assignButton(0, 6);
        const auto pending = pswaker_port_view().pendingControls;
        const auto generation = pswaker_applied_controls().generation;
        const auto recover = [&](PortScreen expected) {
            lx = 255; rx = 0; lt = rt = 255;
            connected = false; sample(PAD_L3 | PAD_R3 | PAD_CROSS); neutralGame();
            assert(pswaker_port_view().screen == PortScreen::InputLost);
            connected = true; sample(PAD_CROSS); neutralGame(); sample(); neutralGame();
            assert(pswaker_port_view().screen == PortScreen::InputLost);
            lx = rx = 128; lt = rt = 0; sample();
            sample(PAD_L3); sample(); // A remapped gameplay button cannot confirm recovery.
            assert(pswaker_port_view().screen == PortScreen::InputLost);
            sample(PAD_CROSS); sample(PAD_CROSS); neutralGame(); sample();
            assert(pswaker_port_view().screen == expected);
            assert(pswaker_port_view().pendingControls == pending);
            assert(pswaker_applied_controls().generation == generation);
        };
        recover(PortScreen::Controls);
        tap(PAD_CROSS); recover(PortScreen::Binding); tap(PAD_CIRCLE);
        tap(PAD_CIRCLE); recover(PortScreen::DiscardControls); tap(PAD_CIRCLE);
        editorRow(9); tap(PAD_CROSS); recover(PortScreen::ApplyingControls);
        failRename = true; sample(); failRename = false; sample();
        assert(pswaker_port_view().screen == PortScreen::ControlsFailed);
        recover(PortScreen::ControlsFailed);
        tap(PAD_CIRCLE); tap(PAD_CIRCLE);
        assert(pswaker_port_view().screen == PortScreen::Game);
        return 0;
    }
    if (std::strncmp(argv[1], "editor-fail-", 12) == 0) {
        const std::string ini = std::string(argv[2]) + "/settings.ini";
        const std::string previous = "# profile\nPSWAKER_LARGE_TEXT=0\n[dev]\nCOS_FPS60=1\n";
        std::ofstream(ini) << previous;
        assert(settings->check());
        const auto applied = pswaker_applied_controls();
        start(); openEditor(); assignButton(0, 6);
        const auto pending = pswaker_port_view().pendingControls;
        const std::string fault = argv[1] + 12;
        failSync = fault == "sync";
        failClose = fault == "close";
        failRename = fault == "rename" || fault == "discard";
        syncCountdown = fault == "uncertain" ? 2 : -1;
        editorRow(9); tap(PAD_CROSS);
        assert(pswaker_port_view().screen == PortScreen::ApplyingControls);
        sample(); neutralGame();
        assert(pswaker_port_view().screen == PortScreen::ControlsFailed);
        assert(!pswaker_port_view().controlsError.empty());
        assert(pswaker_port_view().pendingControls == pending);
        assert(pswaker_applied_controls().config == applied.config);
        assert(pswaker_applied_controls().generation == applied.generation);
        assert(pswaker_applied_controls().legend() == applied.legend());
        // Holding confirm cannot immediately retry; the failure screen needs a fresh release.
        sample(PAD_CROSS); sample(PAD_CROSS); neutralGame();
        assert(pswaker_port_view().screen == PortScreen::ControlsFailed);
        failSync = failClose = failRename = false;
        syncCountdown = -1;
        if (fault == "uncertain") {
            PortSettings disk(argv[2]);
            assert(disk.check() && disk.controls() == pending);
            // Prove Retry rewrites all pending values even if the uncertain file changed.
            std::ofstream(ini) << previous;
        } else assert(readProfile(ini) == previous);
        sample();
        if (fault == "discard") {
            tap(PAD_CIRCLE);
            assert(pswaker_port_view().screen == PortScreen::Settings);
            assert(pswaker_port_view().pendingControls == applied.config);
            assert(pswaker_applied_controls().generation == applied.generation);
            assert(readProfile(ini) == previous);
        } else {
            tap(PAD_CROSS);
            assert(pswaker_port_view().screen == PortScreen::ApplyingControls);
            sample(); sample();
            assert(pswaker_port_view().screen == PortScreen::Controls);
            assert(!pswaker_port_view().controlsDirty && pswaker_port_view().controlsError.empty());
            assert(pswaker_applied_controls().config == pending);
            assert(pswaker_applied_controls().generation == applied.generation + 1);
            PortSettings disk(argv[2]);
            assert(disk.check() && disk.controls() == pending && !disk.largeText());
            tap(PAD_CIRCLE);
        }
        tap(PAD_CIRCLE);
        assert(pswaker_port_view().screen == PortScreen::Game);
        sample(PAD_L3); assert(gamepads[0].button == (fault == "discard" ? 0 : 0x100));
        sample(PAD_CROSS); assert(gamepads[0].button == (fault == "discard" ? 0x100 : 0));
        return 0;
    }
    if (std::strcmp(argv[1], "editor-discard") == 0) {
        assert(settings->check());
        const auto applied = pswaker_applied_controls();
        start(); openEditor();
        assignButton(0, 0); // Selecting the current target is a no-op.
        assert(!pswaker_port_view().controlsDirty);
        assignButton(0, 4); // Unused L1 frees Cross.
        assert(pswaker_port_view().pendingControls.binding(GameAction::B) == ControlTarget::Circle);
        const auto pending = pswaker_port_view().pendingControls;
        tap(PAD_CIRCLE);
        assert(pswaker_port_view().screen == PortScreen::DiscardControls);
        tap(PAD_CIRCLE); // Keep editing, including the pending values.
        assert(pswaker_port_view().screen == PortScreen::Controls);
        assert(pswaker_port_view().pendingControls == pending);
        editorRow(10); tap(PAD_CROSS);
        assert(pswaker_port_view().screen == PortScreen::DiscardControls);
        tap(PAD_CROSS);
        assert(pswaker_port_view().screen == PortScreen::Settings);
        assert(pswaker_port_view().pendingControls == applied.config);
        assert(pswaker_applied_controls().generation == applied.generation);
        assert(!std::filesystem::exists(std::string(argv[2]) + "/settings.ini"));
        tap(PAD_CROSS); // Reopening starts from the complete applied snapshot.
        assert(pswaker_port_view().pendingControls == applied.config);
        tap(PAD_CROSS); tap(PAD_DOWN); tap(PAD_CIRCLE); // Cancel the target picker.
        assert(!pswaker_port_view().controlsDirty);
        tap(PAD_CIRCLE); tap(PAD_CIRCLE);
        assert(pswaker_port_view().screen == PortScreen::Game);
        sample(PAD_CROSS); assert(gamepads[0].button == 0x100);
        return 0;
    }
    if (std::strcmp(argv[1], "editor-apply") == 0) {
        const std::string previous = "# owner settings\nPSWAKER_LARGE_TEXT=0\n[controls]\nversion=1\n"
            "A=L3\nB=R3\nX=L1\nY=Options\nZ=Cross\nStart=Circle\n"
            "invert_camera_x=1\ninvert_camera_y=0\n[dev]\nCOS_FPS60=1\n";
        const auto ini = std::string(argv[2]) + "/settings.ini";
        std::ofstream(ini) << previous;
        assert(settings->check() && pswaker_publish_controls(settings->controls()));
        const auto applied = pswaker_applied_controls();
        start();
        sample(PAD_TOUCH_PAD); sample();
        while (portMenuItems[pswaker_port_view().selection].action != PortAction::EditControls) {
            sample(PAD_DOWN); sample();
        }
        sample(PAD_CROSS); neutralGame(); sample();
        assert(pswaker_port_view().screen == PortScreen::Controls);
        assert(pswaker_port_view().pendingControls == applied.config);
        // A: select the already occupied R3 target. Fixed Cross operates the editor.
        sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::Binding);
        sample(PAD_DOWN); sample(); sample(PAD_CROSS); sample();
        const auto pending = pswaker_port_view().pendingControls;
        assert(pending.binding(GameAction::A) == ControlTarget::R3);
        assert(pending.binding(GameAction::B) == ControlTarget::L3);
        assert(pending.invertCameraX && !pending.invertCameraY);
        assert(pswaker_port_view().controlsDirty);
        assert(pswaker_applied_controls().config == applied.config);
        assert(pswaker_applied_controls().generation == applied.generation);
        assert(pswaker_applied_controls().legend() == applied.legend());
        assert(readProfile(ini) == previous);
        editorRow(9);
        sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::ApplyingControls);
        neutralGame();
        sample();
        assert(pswaker_port_view().screen == PortScreen::Controls);
        assert(!pswaker_port_view().controlsDirty);
        assert(pswaker_applied_controls().config == pending);
        assert(pswaker_applied_controls().generation == applied.generation + 1);
        assert(pswaker_applied_controls().legend()[0] == "GameCube A = R3");
        PortSettings reloaded(argv[2]);
        assert(reloaded.check() && reloaded.controls() == pending && !reloaded.largeText());
        // Back to settings, then explicit resume. Held editor buttons cannot leak.
        sample(); sample(PAD_CIRCLE); neutralGame(); sample();
        assert(pswaker_port_view().screen == PortScreen::Settings);
        sample(PAD_CIRCLE); sample(PAD_CIRCLE); neutralGame();
        sample();
        assert(pswaker_port_view().screen == PortScreen::Game);
        sample(PAD_R3); assert(gamepads[0].button == 0x100);
        sample(PAD_L3); assert(gamepads[0].button == 0x200);
        return 0;
    }
    if (std::strcmp(argv[1], "coherent-snapshot") == 0) {
        const auto defaults = ControlsConfig::defaults();
        auto custom = defaults;
        assert(custom.assign(GameAction::A, ControlTarget::L3));
        assert(custom.assign(GameAction::B, ControlTarget::R3));
        custom.invertCameraX = custom.invertCameraY = true;
        assert(pswaker_publish_controls(defaults));
        std::thread publisher([&] {
            for (unsigned i = 0; i < 2000; ++i)
                assert(pswaker_publish_controls(i % 2 == 0 ? custom : defaults));
        });
        uint64_t previous = 0;
        for (unsigned i = 0; i < 2000; ++i) {
            const auto applied = pswaker_applied_controls();
            assert(applied.generation >= previous);
            assert(applied.config == (applied.generation % 2 == 0 ? custom : defaults));
            previous = applied.generation;
        }
        publisher.join();
        assert(pswaker_applied_controls().generation == 2001);
        return 0;
    }
    if (std::strcmp(argv[1], "profile-defaults") == 0 || std::strcmp(argv[1], "profile-fallback") == 0) {
        PortSettings profile(argv[2]);
        assert(profile.check());
        assert(bool(*profile.controlsFeedback()) == (std::strcmp(argv[1], "profile-fallback") == 0));
        assert(pswaker_publish_controls(profile.controls()));
        const auto applied = pswaker_applied_controls();
        const std::array<std::string, 8> expected{
            "GameCube A = Cross", "GameCube B = Circle", "GameCube X = Square",
            "GameCube Y = Triangle", "GameCube Z = R1", "GameCube Start = Options",
            "Saved camera inversion X: Off", "Saved camera inversion Y: Off"};
        assert(applied.legend() == expected);
        const auto prompt = resolve_ps4_prompt({GameAction::A}, applied);
        assert(prompt.name == "Cross" && prompt.generation == applied.generation);
        start();
        const uint32_t ds4[] = {PAD_CROSS, PAD_CIRCLE, PAD_SQUARE, PAD_TRIANGLE, PAD_R1, PAD_OPTIONS};
        const uint16_t gc[] = {0x100, 0x200, 0x400, 0x800, 0x10, 0x1000};
        for (unsigned i = 0; i < 6; ++i) {
            sample(ds4[i]); assert(gamepads[0].button == gc[i]); sample();
        }
        return 0;
    }
    if (std::strcmp(argv[1], "profile-read-failure") == 0) {
        auto previous = ControlsConfig::defaults();
        assert(previous.assign(GameAction::A, ControlTarget::L3));
        assert(pswaker_publish_controls(previous));
        std::filesystem::create_directory(std::string(argv[2]) + "/settings.ini");
        PortSettings profile(argv[2]);
        assert(!profile.check() && *profile.error());
        assert(pswaker_applied_controls().generation == 1);
        assert(pswaker_applied_controls().legend()[0] == "GameCube A = L3");
        assert(std::filesystem::is_directory(std::string(argv[2]) + "/settings.ini"));
        return 0;
    }
    const bool custom = std::strncmp(argv[1], "custom-", 7) == 0;
    const char* scenario = custom ? argv[1] + 7 : argv[1];
    uint32_t heldActions = PAD_CROSS | PAD_R1;
    uint32_t bButton = PAD_CIRCLE;
    if (custom) {
        std::ofstream(std::string(argv[2]) + "/settings.ini") <<
            "[controls]\nversion=1\nA=L3\nB=R3\nX=L1\nY=Options\nZ=Cross\nStart=Circle\n"
            "invert_camera_x=1\ninvert_camera_y=1\n";
        PortSettings profile(argv[2]);
        assert(profile.check() && !*profile.controlsFeedback());
        assert(pswaker_publish_controls(profile.controls()));
        heldActions = PAD_L3 | PAD_CROSS;
        bButton = PAD_R3;
    }
    if (std::strcmp(argv[1], "all-targets") == 0) {
        // Independent fixture names/wire bits; every action reaches all nine targets.
        const char* names[] = {"Cross", "Circle", "Square", "Triangle", "L1", "R1", "L3", "R3", "Options"};
        const uint32_t bits[] = {0x4000, 0x2000, 0x8000, 0x1000, 0x400, 0x800, 2, 4, 8};
        const char* actions[] = {"A", "B", "X", "Y", "Z", "Start"};
        const uint16_t gc[] = {0x100, 0x200, 0x400, 0x800, 0x10, 0x1000};
        start();
        for (unsigned layout = 0; layout < 9; ++layout) {
            std::string ini = "[controls]\nversion=1\n";
            for (unsigned action = 0; action < 6; ++action)
                ini += std::string(actions[action]) + "=" + names[(layout + action) % 9] + "\n";
            ini += "invert_camera_x=0\ninvert_camera_y=1\n";
            std::ofstream(std::string(argv[2]) + "/settings.ini") << ini;
            PortSettings profile(argv[2]);
            assert(profile.check() && !*profile.controlsFeedback());
            assert(pswaker_publish_controls(profile.controls()));
            const auto applied = pswaker_applied_controls();
            assert(applied.generation == layout + 1);
            assert(!applied.config.invertCameraX && applied.config.invertCameraY);
            for (unsigned target = 0; target < 9; ++target) {
                sample(bits[target]);
                uint16_t expected = 0;
                for (unsigned action = 0; action < 6; ++action)
                    if ((layout + action) % 9 == target) {
                        expected = gc[action];
                        assert(applied.legend()[action] == std::string("GameCube ") + actions[action] + " = " + names[target]);
                    }
                assert(gamepads[0].button == expected);
                assert(gamepads[0].analogA == ((expected & 0x100) ? 255 : 0));
                assert(gamepads[0].analogB == ((expected & 0x200) ? 255 : 0));
                sample();
            }
        }
        return 0;
    }
    if (std::strcmp(argv[1], "assignments") == 0) {
        auto pending = ControlsConfig::defaults();
        const auto previous = pswaker_applied_controls();
        assert(pending.assign(GameAction::B, ControlTarget::Cross)); // Swap occupied A.
        assert(pending.assign(GameAction::Start, ControlTarget::L1)); // Free Options.
        assert(pending.assign(GameAction::Start, ControlTarget::L1)); // No-op.
        pending.invertCameraX = pending.invertCameraY = true;
        assert(pswaker_applied_controls().generation == previous.generation);
        std::ofstream(std::string(argv[2]) + "/settings.ini") << serialize_controls(pending);
        PortSettings profile(argv[2]);
        assert(profile.check() && !*profile.controlsFeedback());
        assert(pswaker_publish_controls(profile.controls()));
        const auto applied = pswaker_applied_controls();
        assert(applied.generation == 1 && previous.generation == 0);
        assert(previous.legend()[0] == "GameCube A = Cross");
        assert(applied.legend()[0] == "GameCube A = Circle");
        assert(applied.legend()[1] == "GameCube B = Cross");
        assert(applied.legend()[5] == "GameCube Start = L1");
        assert(applied.legend()[6] == "Saved camera inversion X: On");
        assert(applied.legend()[7] == "Saved camera inversion Y: On");
        start();
        sample(PAD_CIRCLE); assert(gamepads[0].button == 0x100 && gamepads[0].analogA == 255);
        sample(PAD_CROSS); assert(gamepads[0].button == 0x200 && gamepads[0].analogB == 255);
        sample(PAD_L1); assert(gamepads[0].button == 0x1000);
        sample(PAD_OPTIONS); assert(gamepads[0].button == 0);
        auto invalid = pending;
        invalid.bindings[0] = invalid.bindings[1];
        assert(!pswaker_publish_controls(invalid));
        assert(pswaker_applied_controls().generation == 1);
        sample(PAD_CIRCLE); assert(gamepads[0].button == 0x100);
        assert(pswaker_publish_controls(pending)); // Identical successful publication still advances.
        assert(pswaker_applied_controls().generation == 2);
        assert(applied.generation == 1 && applied.config == pending); // Retained snapshot is stable.
        return 0;
    }
    if (std::strcmp(argv[1], "saved-layout") == 0) {
        std::ofstream(std::string(argv[2]) + "/settings.ini") <<
            "PSWAKER_LARGE_TEXT=0\n[controls]\nversion=1\n"
            "A=L3\nB=R3\nX=L1\nY=Options\nZ=Cross\nStart=Circle\n"
            "invert_camera_x=1\ninvert_camera_y=0\n";
        PortSettings profile(argv[2]);
        assert(profile.check() && !profile.largeText());
        assert(!*profile.controlsFeedback());
        assert(pswaker_publish_controls(profile.controls()));
        const auto applied = pswaker_applied_controls();
        assert(applied.generation == 1);
        assert(applied.config.invertCameraX && !applied.config.invertCameraY);
        assert(applied.legend()[0] == "GameCube A = L3");
        assert(applied.legend()[5] == "GameCube Start = Circle");
        start();
        const uint32_t ds4[] = {PAD_L3, PAD_R3, PAD_L1, PAD_OPTIONS, PAD_CROSS, PAD_CIRCLE};
        const uint16_t gc[] = {0x100, 0x200, 0x400, 0x800, 0x10, 0x1000};
        for (unsigned i = 0; i < 6; ++i) {
            sample(ds4[i]);
            assert(gamepads[0].button == gc[i]);
            assert(gamepads[0].analogA == (i == 0 ? 255 : 0));
            assert(gamepads[0].analogB == (i == 1 ? 255 : 0));
            assert(gamepads[0].stickX == 0 && gamepads[0].substickX == 0);
            sample();
        }
        sample(PAD_R1 | PAD_SQUARE | PAD_TRIANGLE);
        assert(gamepads[0].button == 0);
        return 0;
    }
    if (std::strcmp(scenario, "boot-loss") == 0) {
        assert(pad_open());
        sample(); sample(PAD_CROSS); sample(); // Preparation screens cannot dismiss the legend.
        pswaker_enable_controls(*settings); sample();
        fail = true; sample(); fail = false;
        sample(PAD_CROSS); neutralGame(); // A release from before the failure is invalid.
        assert(pswaker_port_view().screen == PortScreen::InputLost);
        sample(); sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::Legend);
        sample(PAD_CROSS); // Confirm the legend, but lose input before releasing.
        connected = false; sample(); connected = true; sample();
        assert(pswaker_port_view().screen == PortScreen::InputLost);
        sample(PAD_CROSS); neutralGame(); sample();
        assert(pswaker_port_view().screen == PortScreen::Game);
        return 0;
    }
    start();
    if (std::strcmp(argv[1], "text-setting") == 0) {
        PortSettings profile(argv[2]);
        assert(profile.check() && profile.largeText());
        settings = &profile;
        sample(PAD_TOUCH_PAD); sample();
        for (int i = 0; i < 3; ++i) { sample(PAD_DOWN); sample(); }
        sample(PAD_CROSS);
        assert(textChanges == 1);
        assert(!profile.largeText());
        PortSettings reloaded(argv[2]);
        assert(reloaded.check() && !reloaded.largeText());
        sample(PAD_CROSS); sample(PAD_CROSS);
        assert(textChanges == 1); // A held confirm must not issue repeated writes.
        neutralGame();
        assert(pswaker_port_view().screen == PortScreen::Settings);
        sample(); sample(PAD_CROSS);
        assert(textChanges == 2);
        assert(profile.largeText());
        sample(); sample(PAD_CIRCLE); sample();
        assert(pswaker_port_view().screen == PortScreen::Game);
        return 0;
    }
    if (std::strcmp(scenario, "fault-check") == 0) {
        sample(PAD_TOUCH_PAD); sample();
        sample(PAD_DOWN); sample(); sample(PAD_DOWN); sample();
        sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::Game);
        lx = 255; lt = rt = 255;
        sample(heldActions);
        assert(gamepads[0].button == 0x170 && gamepads[0].stickX == 127);
        clockValue += 5;
        sample(heldActions); // Delayed failure interrupts active held input.
        neutralGame();
        assert(pswaker_port_view().screen == PortScreen::InputLost);
        sample(PAD_CROSS); neutralGame(); // Real reads recover, still paused.
        lx = 128; lt = rt = 0; sample(); sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::Game);
        return 0;
    }
    if (std::strcmp(scenario, "menus") == 0) {
        sample(PAD_TOUCH_PAD); neutralGame();
        assert(pswaker_port_view().screen == PortScreen::Settings);
        sample(); sample(PAD_DOWN); sample(); sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::Legend);
        sample(PAD_CIRCLE); sample();
        assert(pswaker_port_view().screen == PortScreen::Settings);
        sample(PAD_CIRCLE); neutralGame(); sample();
        assert(pswaker_port_view().screen == PortScreen::Game);
        sample(PAD_TOUCH_PAD); sample();
        for (int i = 0; i < 4; ++i) { sample(PAD_DOWN); sample(); }
        sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::Quit);
        sample(PAD_CIRCLE); sample(); // Cancel exit, never quit from Circle.
        assert(pswaker_port_view().screen == PortScreen::Settings);
        sample(PAD_CROSS); sample(); sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::Exit);
        neutralGame();
        return 0;
    }
    if (std::strcmp(scenario, "disconnect") == 0 || std::strcmp(scenario, "failed-read") == 0) {
        lx = 255; lt = rt = 255;
        sample(heldActions);
        assert(gamepads[0].button == 0x170 && gamepads[0].stickX == 127);
        if (std::strcmp(scenario, "disconnect") == 0) connected = false;
        else fail = true; // The API returns failure while still writing held input.
        sample(heldActions);
        neutralGame();
        assert(pswaker_port_view().screen == PortScreen::InputLost);
        connected = true; fail = false;
        sample(PAD_CROSS); neutralGame();
        sample(); neutralGame(); // Still holding movement and triggers.
        assert(pswaker_port_view().screen == PortScreen::InputLost);
        lx = 128; lt = rt = 0;
        sample(); neutralGame();
        // A second loss invalidates the previous release.
        fail = true; sample(); fail = false; sample(PAD_CROSS); sample();
        assert(pswaker_port_view().screen == PortScreen::InputLost);
        sample(PAD_CROSS); neutralGame();
        sample();
        assert(pswaker_port_view().screen == PortScreen::Game);
        sample(bButton);
        assert(gamepads[0].button == 0x200);
        return 0;
    }
    if (std::strcmp(scenario, "mapping") == 0) {
        const uint32_t ds4[] = {PAD_CROSS, PAD_CIRCLE, PAD_SQUARE, PAD_TRIANGLE,
                              PAD_R1, PAD_OPTIONS, PAD_UP, PAD_DOWN, PAD_LEFT, PAD_RIGHT};
        const uint16_t gc[] = {0x100, 0x200, 0x400, 0x800, 0x10, 0x1000, 8, 4, 1, 2};
        for (unsigned i = 0; i < 10; ++i) {
            if (custom && i < 6) continue; // Remappable actions are covered by the focused layouts.
            sample(ds4[i]); assert(gamepads[0].button == gc[i]); sample();
        }
        lx = 255; ly = 0; rx = 0; ry = 255; lt = 128; rt = 229;
        sample();
        assert(gamepads[0].stickX == 127 && gamepads[0].stickY == 127);
        assert(gamepads[0].substickX == -127 && gamepads[0].substickY == -127);
        assert(gamepads[0].triggerLeft == 128 && gamepads[0].triggerRight == 229);
        assert(gamepads[0].button == 0);
        lt = 230; rt = 255; sample();
        assert(gamepads[0].button == 0x60);
        assert(gamepads[0].triggerLeft == 230 && gamepads[0].triggerRight == 255);
        return 0;
    }
    assert(std::strcmp(argv[1], "legend") == 0);
}
