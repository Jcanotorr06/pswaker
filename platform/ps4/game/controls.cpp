#include "controls.hpp"
#include "storage.hpp"
#include "native/platform.h"
#include "frame-pacing.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <mutex>

namespace {
std::mutex appliedMutex;
AppliedControls applied;
bool checkAfterResume = false;
double failReadAt = -1;
bool enabled = false;
PortView view{PortScreen::Legend, 0, false, false};
pad current{};
bool armed = false;
PortScreen destination = PortScreen::Game;
PortScreen beforeLoss = PortScreen::Legend;
PortScreen afterLegend = PortScreen::Game;
PortSettings* settings = nullptr;

const char* screenName(PortScreen screen) {
    constexpr const char* names[] = {"legend", "game", "settings", "quit", "input-lost", "exit",
        "controls", "binding", "discard-controls", "applying-controls", "controls-failed", "restore-controls"};
    return names[static_cast<unsigned>(screen)];
}

void enter(PortScreen screen) {
    if (view.screen == screen) return;
    say("INPUT screen=%s->%s connected=%d; gameplay neutral outside Game", screenName(view.screen), screenName(screen), view.connected);
    if (screen != PortScreen::Game) pad_player_vibrate(0, 0, 0);
    view.screen = screen;
    armed = false;
}

extern "C" int __real_scePadReadState(int32_t handle, void* data);
extern "C" int __wrap_scePadReadState(int32_t handle, void* data) {
    if (failReadAt >= 0 && now_seconds() >= failReadAt) {
        failReadAt = -1;
        say("INPUT CHECK injected scePadReadState failure; native reader must neutralize and pause");
        return -1;
    }
    return __real_scePadReadState(handle, data);
}

bool neutral() {
    return current.held == 0 && current.left_x == 0 && current.left_y == 0 &&
           current.right_x == 0 && current.right_y == 0 && current.l2 == 0 && current.r2 == 0;
}
}

AppliedControls pswaker_applied_controls() {
    const std::lock_guard lock(appliedMutex);
    return applied;
}
bool pswaker_publish_controls(const ControlsConfig& config) {
    if (!config.valid()) return false;
    const std::lock_guard lock(appliedMutex);
    if (applied.generation == std::numeric_limits<uint64_t>::max()) return false;
    applied = {config, applied.generation + 1};
    return true;
}
std::array<std::string, 8> AppliedControls::legend() const {
    std::array<std::string, 8> lines;
    for (const auto action : gameActions)
        lines[static_cast<unsigned>(action)] = std::string("GameCube ") + control_action_name(action) + " = " +
                                              control_target_name(config.binding(action));
    lines[6] = std::string("Saved camera inversion X: ") + (config.invertCameraX ? "On" : "Off");
    lines[7] = std::string("Saved camera inversion Y: ") + (config.invertCameraY ? "On" : "Off");
    return lines;
}

PortView pswaker_port_view() {
    auto result = view;
    result.controlsDirty = result.pendingControls != pswaker_applied_controls().config;
    return result;
}
void pswaker_enable_controls(PortSettings& profile) { settings = &profile; enabled = true; }

void pswaker_poll_controls() {
    pad first{};
    pad_poll(&first);
    view.connected = pad_player(0, &current);
    if (!enabled) return;
    if (!view.connected) {
        if (view.screen != PortScreen::InputLost)
            beforeLoss = view.releasing ? destination : view.screen;
        enter(PortScreen::InputLost);
        view.releasing = false;
        armed = false;
        return;
    }
    if (view.releasing) {
        if (neutral()) {
            enter(destination);
            if (checkAfterResume && destination == PortScreen::Game) {
                checkAfterResume = false;
                failReadAt = now_seconds() + 5;
                say("INPUT CHECK resumed; one native read will fail in 5 seconds; hold inputs now");
            }
            view.releasing = false;
            armed = true; // This fresh neutral sample also releases the destination screen.
        }
        return;
    }
    if (view.screen == PortScreen::Game) {
        if (current.held & PAD_TOUCH_PAD) {
            view.selection = 0;
            enter(PortScreen::Settings);
        }
        return;
    }
    if (view.screen == PortScreen::ApplyingControls) {
        view.controlsError.clear();
        if (!view.pendingControls.valid() || pswaker_applied_controls().generation == std::numeric_limits<uint64_t>::max())
            view.controlsError = "The controls configuration could not be applied.";
        else if (!settings->setControls(view.pendingControls)) view.controlsError = settings->error();
        else if (!pswaker_publish_controls(view.pendingControls)) view.controlsError = "Saved controls could not be published.";
        say("CONTROLS apply-confirmed=%d generation=%llu error=%s", view.controlsError.empty(),
            static_cast<unsigned long long>(pswaker_applied_controls().generation), view.controlsError.c_str());
        enter(view.controlsError.empty() ? PortScreen::Controls : PortScreen::ControlsFailed);
        return;
    }
    if (neutral()) armed = true;
    if (!armed) return;
    const bool cross = current.held & PAD_CROSS;
    const bool circle = current.held & PAD_CIRCLE;
    if (view.screen == PortScreen::Settings && (current.held & (PAD_UP | PAD_DOWN))) {
        const unsigned count = portMenuItems.size();
        view.selection = (view.selection + ((current.held & PAD_DOWN) ? 1 : count - 1)) % count;
        armed = false;
        return;
    }
    if ((view.screen == PortScreen::Controls || view.screen == PortScreen::Binding) &&
        (current.held & (PAD_UP | PAD_DOWN))) {
        auto& selection = view.screen == PortScreen::Controls ? view.controlsSelection : view.bindingSelection;
        const unsigned count = view.screen == PortScreen::Controls ? gameActions.size() + 3 : 9;
        selection = (selection + ((current.held & PAD_DOWN) ? 1 : count - 1)) % count;
        armed = false;
        return;
    }
    destination = view.screen;
    const auto action = portMenuItems[view.selection].action;
    switch (view.screen) {
    case PortScreen::Legend:
        if (cross || (circle && afterLegend == PortScreen::Settings)) destination = afterLegend;
        break;
    case PortScreen::InputLost:
        if (cross) destination = beforeLoss;
        break;
    case PortScreen::Settings:
        if (circle || (cross && action == PortAction::Resume)) destination = PortScreen::Game;
        else if (cross && action == PortAction::ShowLegend) {
            afterLegend = PortScreen::Settings;
            destination = PortScreen::Legend;
        } else if (cross && action == PortAction::CheckFailedRead) {
            checkAfterResume = true;
            destination = PortScreen::Game;
        } else if (cross && action == PortAction::ToggleText) {
            pswaker_toggle_text_size();
            armed = false;
        } else if (cross && action == PortAction::EditControls) {
            view.pendingControls = pswaker_applied_controls().config;
            view.controlsSelection = 0;
            view.controlsError.clear();
            destination = PortScreen::Controls;
        } else if (cross && action == PortAction::Quit) destination = PortScreen::Quit;
        else if (cross && (action == PortAction::SampleOutset || action == PortAction::SampleForest)) {
            pswaker_perf_arm(action == PortAction::SampleOutset ? "outset" : "forest");
            destination = PortScreen::Game;
        } else if (cross && (action == PortAction::Transition || action == PortAction::Gameplay)) {
            pswaker_perf_phase(action == PortAction::Transition ? "transition" : "gameplay");
            destination = PortScreen::Game;
        }
        break;
    case PortScreen::Quit:
        if (circle) destination = PortScreen::Settings;
        else if (cross) destination = PortScreen::Exit;
        break;
    case PortScreen::Controls:
        if (circle || (cross && view.controlsSelection == gameActions.size() + 2))
            destination = view.pendingControls == pswaker_applied_controls().config ? PortScreen::Settings : PortScreen::DiscardControls;
        else if (cross && view.controlsSelection < gameActions.size()) {
            view.bindingSelection = static_cast<unsigned>(view.pendingControls.binding(gameActions[view.controlsSelection]));
            destination = PortScreen::Binding;
        } else if (cross && view.controlsSelection == gameActions.size()) destination = PortScreen::RestoreControls;
        else if (cross) destination = PortScreen::ApplyingControls;
        break;
    case PortScreen::RestoreControls:
        if (circle) destination = PortScreen::Controls;
        else if (cross) {
            view.pendingControls = ControlsConfig::defaults();
            destination = PortScreen::Controls;
        }
        break;
    case PortScreen::Binding:
        if (circle) destination = PortScreen::Controls;
        else if (cross) {
            view.pendingControls.assign(gameActions[view.controlsSelection], static_cast<ControlTarget>(view.bindingSelection));
            destination = PortScreen::Controls;
        }
        break;
    case PortScreen::DiscardControls:
        if (circle) destination = PortScreen::Controls;
        else if (cross) {
            view.pendingControls = pswaker_applied_controls().config;
            view.controlsError.clear();
            destination = PortScreen::Settings;
        }
        break;
    case PortScreen::ControlsFailed:
        if (cross) destination = PortScreen::ApplyingControls;
        else if (circle) {
            view.pendingControls = pswaker_applied_controls().config;
            view.controlsError.clear();
            destination = PortScreen::Settings;
        }
        break;
    default: break;
    }
    if (destination != view.screen) {
        say("INPUT explicit-confirm screen=%s destination=%s; waiting for neutral release", screenName(view.screen), screenName(destination));
        view.releasing = true;
        armed = false;
    }
}

extern "C" u32 pswaker_read_gamepad(PADStatus* status) {
    for (unsigned i = 0; i < PAD_CHANMAX; ++i) {
        status[i] = {};
        status[i].err = i == 0 && view.connected ? PAD_ERR_NONE : PAD_ERR_NO_CONTROLLER;
    }
    if (!view.connected || view.screen != PortScreen::Game || view.releasing) return 0;
    auto& p = status[0];
    const auto snapshot = pswaker_applied_controls();
    constexpr std::array<uint32_t, 9> targets{PAD_CROSS, PAD_CIRCLE, PAD_SQUARE, PAD_TRIANGLE,
        PAD_L1, PAD_R1, PAD_L3, PAD_R3, PAD_OPTIONS};
    constexpr std::array<uint16_t, 6> actions{PAD_BUTTON_A, PAD_BUTTON_B, PAD_BUTTON_X,
        PAD_BUTTON_Y, PAD_TRIGGER_Z, PAD_BUTTON_START};
    for (const auto action : gameActions)
        if (current.held & targets[static_cast<unsigned>(snapshot.config.binding(action))])
            p.button |= actions[static_cast<unsigned>(action)];
    constexpr struct { uint32_t ds4; uint16_t gc; } mapping[] = {
        {PAD_UP, PAD_BUTTON_UP}, {PAD_DOWN, PAD_BUTTON_DOWN},
        {PAD_LEFT, PAD_BUTTON_LEFT}, {PAD_RIGHT, PAD_BUTTON_RIGHT},
    };
    for (const auto& button : mapping)
        if (current.held & button.ds4) p.button |= button.gc;
    const auto stick = [](float value) { return static_cast<s8>(std::lround(std::clamp(value, -1.f, 1.f) * 127)); };
    p.stickX = stick(current.left_x); p.stickY = stick(-current.left_y);
    p.substickX = stick(current.right_x); p.substickY = stick(-current.right_y);
    p.triggerLeft = static_cast<u8>(std::lround(current.l2 * 255));
    p.triggerRight = static_cast<u8>(std::lround(current.r2 * 255));
    // First representable sample at/above 90% is 230/255. Keep analog travel intact.
    if (current.l2 >= .9f) p.button |= PAD_TRIGGER_L;
    if (current.r2 >= .9f) p.button |= PAD_TRIGGER_R;
    p.analogA = (p.button & PAD_BUTTON_A) ? 255 : 0;
    p.analogB = (p.button & PAD_BUTTON_B) ? 255 : 0;
    return PAD_CHAN0_BIT;
}

void pswaker_log_controls() {
    static double next = 0;
    const double now = now_seconds();
    if (now < next) return;
    const auto diagnosticStart = pswaker_perf_now();
    next = now + 1;
    PADStatus status[PAD_CHANMAX];
    pswaker_read_gamepad(status);
    const auto& p = status[0];
    say("INPUT sample connected=%d screen=%s releasing=%d raw-buttons=%#x sticks=%.3f,%.3f,%.3f,%.3f triggers=%.3f,%.3f game-buttons=%#x game-sticks=%d,%d,%d,%d game-triggers=%u,%u threshold=90%%",
        view.connected, screenName(view.screen), view.releasing, current.held,
        current.left_x, current.left_y, current.right_x, current.right_y, current.l2, current.r2,
        p.button, p.stickX, p.stickY, p.substickX, p.substickY, p.triggerLeft, p.triggerRight);
    pswaker_perf_diagnostic(PswakerDiagnostic::Input, diagnosticStart);
}
