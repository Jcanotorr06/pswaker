// Only the external console service boundary is simulated. No game data or GPU.
#include "controls.hpp"
#include "storage.hpp"
#include "frame-pacing.hpp"
#include "native/platform.h"
#include <cassert>
#include <cstdint>
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
unsigned textChanges = 0;
PortSettings* settings = nullptr;
double clockValue = 1000;
PADStatus gamepads[PAD_CHANMAX];

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
    pswaker_enable_controls();
    sample(PAD_CROSS); // Held during first launch must not confirm.
    assert(pswaker_port_view().screen == PortScreen::Legend);
    neutralGame();
    sample(); sample(PAD_CROSS);
    neutralGame(); // Confirmation is consumed, even before release.
    sample();
    assert(pswaker_port_view().screen == PortScreen::Game);
    assert(gamepads[0].button == 0);
}
}
extern "C" {
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
int main(int argc, char** argv) {
    assert(argc == 3);
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
        pswaker_enable_controls(); sample();
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
