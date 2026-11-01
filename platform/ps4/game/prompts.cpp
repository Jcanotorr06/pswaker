#include "prompts.hpp"
#include <algorithm>
#include <vector>

namespace {
constexpr std::array<Ps4Icon, 9> targetIcons{Ps4Icon::Cross, Ps4Icon::Circle, Ps4Icon::Square,
    Ps4Icon::Triangle, Ps4Icon::L1, Ps4Icon::R1, Ps4Icon::L3, Ps4Icon::R3, Ps4Icon::Options};
struct PromptAdapter {
    void* context;
    PromptRefreshCallback refresh;
    std::optional<uint64_t> generation;
};
std::vector<PromptAdapter> adapters;
}

PromptResult resolve_ps4_prompt(const PromptRequest& request, const AppliedControls& applied,
                               PromptIconAvailable available) {
    PromptResult result;
    result.generation = applied.generation;
    result.gesture = request.gesture;
    result.variant = request.variant;
    result.direction = request.direction;
    const auto unresolved = [&](const char* reason) {
        result.status = PromptStatus::Unresolved;
        result.icon.reset();
        result.name.clear();
        result.reason = reason;
        return result;
    };
    if (static_cast<unsigned>(request.context) > static_cast<unsigned>(PromptContext::PortMenu) ||
        static_cast<unsigned>(request.gesture) > static_cast<unsigned>(PromptGesture::Hold) ||
        static_cast<unsigned>(request.variant) > static_cast<unsigned>(PromptVariant::Trigger) ||
        static_cast<unsigned>(request.direction) > static_cast<unsigned>(PromptDirection::DownRight))
        return unresolved("Unknown prompt context, gesture, variant or direction");
    if ((request.variant == PromptVariant::Direction) != (request.direction != PromptDirection::None))
        return unresolved("Directional prompts require exactly one direction");

    Ps4Icon icon;
    bool button = false, stick = false, dpad = false, trigger = false;
    if (const auto* action = std::get_if<GameAction>(&request.control)) {
        if (static_cast<unsigned>(*action) >= gameActions.size())
            return unresolved("Unknown game action");
        if (request.context == PromptContext::PortMenu) {
            switch (*action) {
            case GameAction::A: icon = Ps4Icon::Cross; result.name = "Cross"; break;
            case GameAction::B: icon = Ps4Icon::Circle; result.name = "Circle"; break;
            case GameAction::Start: icon = Ps4Icon::Touchpad; result.name = "Touchpad click"; break;
            default: return unresolved("No fixed port-menu meaning for this game action");
            }
        } else {
            if (!applied.config.valid()) return unresolved("Invalid applied bindings");
            const auto target = applied.config.binding(*action);
            result.name = control_target_name(target);
            icon = targetIcons[static_cast<unsigned>(target)];
        }
        button = true;
    } else {
        const auto fixed = std::get<FixedControl>(request.control);
        if (request.context == PromptContext::PortMenu && fixed != FixedControl::DPad &&
            fixed != FixedControl::PortConfirm && fixed != FixedControl::PortCancel && fixed != FixedControl::PortSettings)
            return unresolved("This gameplay control has no fixed port-menu meaning");
        if (request.context != PromptContext::PortMenu &&
            (fixed == FixedControl::PortConfirm || fixed == FixedControl::PortCancel || fixed == FixedControl::PortSettings))
            return unresolved("Fixed port instructions require port-menu context");
        switch (fixed) {
        case FixedControl::MainStick: icon = Ps4Icon::LeftStick; result.name = "Left stick"; stick = true; break;
        case FixedControl::CStick: icon = Ps4Icon::RightStick; result.name = "Right stick"; stick = true; break;
        case FixedControl::DPad: icon = Ps4Icon::DPad; result.name = "D-pad"; dpad = true; break;
        case FixedControl::LTrigger: icon = Ps4Icon::L2; result.name = "L2"; trigger = true; break;
        case FixedControl::RTrigger: icon = Ps4Icon::R2; result.name = "R2"; trigger = true; break;
        case FixedControl::PortConfirm: icon = Ps4Icon::Cross; result.name = "Cross"; button = true; break;
        case FixedControl::PortCancel: icon = Ps4Icon::Circle; result.name = "Circle"; button = true; break;
        case FixedControl::PortSettings: icon = Ps4Icon::Touchpad; result.name = "Touchpad click"; button = true; break;
        default: return unresolved("Unknown fixed control");
        }
    }
    switch (request.variant) {
    case PromptVariant::Button:
        if (!button && !dpad) return unresolved("Movement and analog travel require an explicit variant");
        break;
    case PromptVariant::StickClick:
        if (!button || (icon != Ps4Icon::L3 && icon != Ps4Icon::R3))
            return unresolved("Stick clicks must name an action applied to L3 or R3");
        break;
    case PromptVariant::StickMove:
        if (!stick) return unresolved("Stick movement requires a fixed stick");
        result.name += " movement";
        break;
    case PromptVariant::Direction: {
        if (!stick && !dpad) return unresolved("Directions require a fixed stick or D-pad");
        constexpr const char* directions[]{"", "up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"};
        result.name += std::string(" ") + directions[static_cast<unsigned>(request.direction)];
        break;
    }
    case PromptVariant::RotateClockwise:
    case PromptVariant::RotateCounterclockwise:
    case PromptVariant::OscillateHorizontal:
    case PromptVariant::OscillateVertical:
        if (!stick) return unresolved("Stick animation requires a fixed stick");
        if (request.variant == PromptVariant::RotateClockwise) result.name += " clockwise";
        if (request.variant == PromptVariant::RotateCounterclockwise) result.name += " counterclockwise";
        if (request.variant == PromptVariant::OscillateHorizontal) result.name += " left / right";
        if (request.variant == PromptVariant::OscillateVertical) result.name += " up / down";
        break;
    case PromptVariant::TriggerPartial:
    case PromptVariant::TriggerFull:
        if (!trigger) return unresolved("Analog travel requires a fixed L2 or R2 trigger");
        result.name += request.variant == PromptVariant::TriggerPartial ?
            " partial press (below 90% travel)" : " full press (90% travel or more)";
        break;
    case PromptVariant::Trigger:
        if (!trigger) return unresolved("Trigger prompts require a fixed L2 or R2 trigger");
        break;
    }
    result.icon = available && available(icon) ? std::optional(icon) : std::nullopt;
    result.status = result.icon ? PromptStatus::Icon : PromptStatus::TextFallback;
    return result;
}

std::array<std::string, 8> AppliedControls::legend() const {
    std::array<std::string, 8> lines;
    for (const auto action : gameActions)
        lines[static_cast<unsigned>(action)] = std::string("GameCube ") + control_action_name(action) + " = " +
            resolve_ps4_prompt({action}, *this).name;
    lines[6] = std::string("Saved camera inversion X: ") + (config.invertCameraX ? "On" : "Off");
    lines[7] = std::string("Saved camera inversion Y: ") + (config.invertCameraY ? "On" : "Off");
    return lines;
}

std::array<std::string, 3> AppliedControls::fixedGameplay() const {
    const auto left = resolve_ps4_prompt({FixedControl::MainStick, PromptContext::Gameplay,
        PromptGesture::Press, PromptVariant::StickMove}, *this);
    const auto right = resolve_ps4_prompt({FixedControl::CStick, PromptContext::Gameplay,
        PromptGesture::Press, PromptVariant::StickMove}, *this);
    const auto dpad = resolve_ps4_prompt({FixedControl::DPad}, *this);
    const auto l2 = resolve_ps4_prompt({FixedControl::LTrigger, PromptContext::Gameplay,
        PromptGesture::Press, PromptVariant::TriggerFull}, *this);
    const auto r2 = resolve_ps4_prompt({FixedControl::RTrigger, PromptContext::Gameplay,
        PromptGesture::Press, PromptVariant::TriggerFull}, *this);
    return {left.name + " = Control Stick; " + right.name + " = C Stick; " + dpad.name + " = D-pad",
        l2.name + "; " + r2.name + ". Partial travel stays analog.",
        "L3 / R3 assignments are digital only; stick movement stays fixed."};
}

std::array<std::string, 2> AppliedControls::fixedPort() const {
    const auto name = [&](FixedControl control) {
        return resolve_ps4_prompt({control, PromptContext::PortMenu}, *this).name;
    };
    return {name(FixedControl::PortSettings) + " = Port settings; " + name(FixedControl::DPad) + " = Navigate",
        name(FixedControl::PortConfirm) + " = Confirm; " + name(FixedControl::PortCancel) + " = Cancel / Back"};
}

bool pswaker_register_prompt_adapter(void* context, PromptRefreshCallback refresh) {
    if (!refresh || std::any_of(adapters.begin(), adapters.end(), [&](const auto& adapter) {
            return adapter.context == context && adapter.refresh == refresh;
        })) return false;
    adapters.push_back({context, refresh, std::nullopt});
    return true;
}

bool pswaker_refresh_prompts(const AppliedControls& applied) {
    bool ready = true;
    for (auto& adapter : adapters) {
        if (adapter.generation == applied.generation) continue;
        if (adapter.refresh(adapter.context, applied)) adapter.generation = applied.generation;
        else ready = false;
    }
    return ready;
}
