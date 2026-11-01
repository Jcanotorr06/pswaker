// Exercise only public requests/results. No game headers, assets or GPU.
#include "prompts.hpp"
#include <cassert>
#include <array>

bool allIcons(Ps4Icon) { return true; }
bool faceIcons(Ps4Icon icon) { return icon == Ps4Icon::Cross || icon == Ps4Icon::Circle; }

int main() {
    const AppliedControls applied{ControlsConfig::defaults(), 17};
    const auto result = resolve_ps4_prompt({GameAction::A}, applied);
    assert(result.status == PromptStatus::TextFallback);
    assert(result.name == "Cross" && !result.icon);
    assert(result.generation == 17 && result.reason.empty());
    const char* defaults[]{"Cross", "Circle", "Square", "Triangle", "R1", "Options"};
    for (unsigned action = 0; action < 6; ++action)
        assert(resolve_ps4_prompt({static_cast<GameAction>(action)}, applied).name == defaults[action]);

    constexpr std::array<const char*, 9> names{
        "Cross", "Circle", "Square", "Triangle", "L1", "R1", "L3", "R3", "Options"};
    constexpr std::array<Ps4Icon, 9> icons{Ps4Icon::Cross, Ps4Icon::Circle, Ps4Icon::Square,
        Ps4Icon::Triangle, Ps4Icon::L1, Ps4Icon::R1, Ps4Icon::L3, Ps4Icon::R3, Ps4Icon::Options};
    for (const auto action : gameActions) {
        for (unsigned target = 0; target < names.size(); ++target) {
            auto custom = applied;
            assert(custom.config.assign(action, static_cast<ControlTarget>(target)));
            for (const auto context : {PromptContext::Gameplay, PromptContext::NativeGameMenu}) {
                for (const auto gesture : {PromptGesture::Press, PromptGesture::Hold}) {
                    const PromptRequest request{action, context, gesture};
                    const auto icon = resolve_ps4_prompt(request, custom, allIcons);
                    assert(icon.status == PromptStatus::Icon && icon.icon == icons[target]);
                    assert(icon.name == names[target] && icon.generation == 17);
                    assert(icon.gesture == gesture && icon.variant == PromptVariant::Button);
                    const auto text = resolve_ps4_prompt(request, custom);
                    assert(text.status == PromptStatus::TextFallback && !text.icon);
                    assert(text.name == icon.name && text.gesture == gesture);
                }
            }
        }
    }

    auto custom = applied;
    assert(custom.config.assign(GameAction::A, ControlTarget::R3));
    assert(custom.config.assign(GameAction::B, ControlTarget::L3));
    assert(custom.config.assign(GameAction::Start, ControlTarget::L1));
    for (const auto context : {PromptContext::Gameplay, PromptContext::NativeGameMenu}) {
        const auto click = resolve_ps4_prompt({GameAction::A, context,
            PromptGesture::Hold, PromptVariant::StickClick}, custom, allIcons);
        assert(click.name == "R3" && click.icon == Ps4Icon::R3);
        assert(click.gesture == PromptGesture::Hold && click.variant == PromptVariant::StickClick);
    }
    // Accepted alternatives retain their own gesture and applied binding.
    const std::array<PromptRequest, 2> alternatives{{{GameAction::A},
        {GameAction::B, PromptContext::Gameplay, PromptGesture::Hold}}};
    assert(resolve_ps4_prompt(alternatives[0], custom).name == "R3");
    const auto second = resolve_ps4_prompt(alternatives[1], custom);
    assert(second.name == "L3" && second.gesture == PromptGesture::Hold);

    for (const auto action : {GameAction::A, GameAction::B, GameAction::Start}) {
        const auto port = resolve_ps4_prompt({action, PromptContext::PortMenu}, custom, faceIcons);
        if (action == GameAction::A) assert(port.name == "Cross" && port.icon == Ps4Icon::Cross);
        if (action == GameAction::B) assert(port.name == "Circle" && port.icon == Ps4Icon::Circle);
        if (action == GameAction::Start) assert(port.name == "Touchpad click" && !port.icon);
        assert(port.generation == 17);
    }

    struct FixedCase { FixedControl control; PromptVariant variant; PromptDirection direction;
        const char* name; Ps4Icon icon; };
    const FixedCase fixed[]{
        {FixedControl::MainStick, PromptVariant::StickMove, PromptDirection::None, "Left stick movement", Ps4Icon::LeftStick},
        {FixedControl::CStick, PromptVariant::StickMove, PromptDirection::None, "Right stick movement", Ps4Icon::RightStick},
        {FixedControl::DPad, PromptVariant::Button, PromptDirection::None, "D-pad", Ps4Icon::DPad},
        {FixedControl::MainStick, PromptVariant::Direction, PromptDirection::Up, "Left stick up", Ps4Icon::LeftStick},
        {FixedControl::CStick, PromptVariant::Direction, PromptDirection::DownLeft, "Right stick down-left", Ps4Icon::RightStick},
        {FixedControl::DPad, PromptVariant::Direction, PromptDirection::Right, "D-pad right", Ps4Icon::DPad},
        {FixedControl::MainStick, PromptVariant::RotateClockwise, PromptDirection::None, "Left stick clockwise", Ps4Icon::LeftStick},
        {FixedControl::CStick, PromptVariant::RotateCounterclockwise, PromptDirection::None, "Right stick counterclockwise", Ps4Icon::RightStick},
        {FixedControl::MainStick, PromptVariant::OscillateHorizontal, PromptDirection::None, "Left stick left / right", Ps4Icon::LeftStick},
        {FixedControl::CStick, PromptVariant::OscillateVertical, PromptDirection::None, "Right stick up / down", Ps4Icon::RightStick},
        {FixedControl::LTrigger, PromptVariant::TriggerPartial, PromptDirection::None, "L2 partial press (below 90% travel)", Ps4Icon::L2},
        {FixedControl::LTrigger, PromptVariant::TriggerFull, PromptDirection::None, "L2 full press (90% travel or more)", Ps4Icon::L2},
        {FixedControl::RTrigger, PromptVariant::TriggerPartial, PromptDirection::None, "R2 partial press (below 90% travel)", Ps4Icon::R2},
        {FixedControl::RTrigger, PromptVariant::TriggerFull, PromptDirection::None, "R2 full press (90% travel or more)", Ps4Icon::R2},
        // GameCube L/R used as buttons: a plain press, without a full-travel requirement.
        {FixedControl::LTrigger, PromptVariant::TriggerPress, PromptDirection::None, "L2", Ps4Icon::L2},
        {FixedControl::RTrigger, PromptVariant::TriggerPress, PromptDirection::None, "R2", Ps4Icon::R2},
    };
    for (const auto& example : fixed) {
        for (const auto context : {PromptContext::Gameplay, PromptContext::NativeGameMenu}) {
            for (const auto gesture : {PromptGesture::Press, PromptGesture::Hold}) {
                const PromptRequest request{example.control, context, gesture, example.variant, example.direction};
                const auto answer = resolve_ps4_prompt(request, custom, allIcons);
                assert(answer.status == PromptStatus::Icon && answer.icon == example.icon);
                assert(answer.name == example.name && answer.generation == 17);
                assert(answer.gesture == gesture && answer.variant == example.variant && answer.direction == example.direction);
                const auto fallback = resolve_ps4_prompt(request, custom, faceIcons);
                assert(fallback.status == PromptStatus::TextFallback && !fallback.icon && fallback.name == example.name);
            }
        }
    }
    const std::array<FixedControl, 3> portControls{
        FixedControl::PortConfirm, FixedControl::PortCancel, FixedControl::PortSettings};
    const char* portNames[]{"Cross", "Circle", "Touchpad click"};
    for (unsigned i = 0; i < portControls.size(); ++i)
        assert(resolve_ps4_prompt({portControls[i], PromptContext::PortMenu}, custom).name == portNames[i]);
    const char* directions[]{"up", "down", "left", "right", "up-left", "up-right", "down-left", "down-right"};
    for (unsigned i = 0; i < 8; ++i) {
        const auto directed = resolve_ps4_prompt({FixedControl::MainStick, PromptContext::Gameplay,
            PromptGesture::Press, PromptVariant::Direction, static_cast<PromptDirection>(i + 1)}, custom);
        assert(directed.name == std::string("Left stick ") + directions[i]);
    }

    const PromptRequest unsupported[]{
        {static_cast<GameAction>(99)}, {static_cast<FixedControl>(99)},
        {GameAction::A, static_cast<PromptContext>(99)},
        {GameAction::A, PromptContext::Gameplay, static_cast<PromptGesture>(99)},
        {GameAction::A, PromptContext::Gameplay, PromptGesture::Press, static_cast<PromptVariant>(99)},
        {FixedControl::MainStick, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::Direction},
        {FixedControl::DPad, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::Direction, static_cast<PromptDirection>(99)},
        {GameAction::X, PromptContext::PortMenu},
        {FixedControl::MainStick}, {FixedControl::MainStick, PromptContext::PortMenu},
        {FixedControl::MainStick, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::StickClick},
        {FixedControl::PortConfirm}, {FixedControl::LTrigger},
        {GameAction::X, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::StickClick},
        {GameAction::A, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::Direction, PromptDirection::Up},
        {GameAction::A, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::TriggerPartial},
        {FixedControl::DPad, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::RotateClockwise},
        {GameAction::Z, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::TriggerPress},
        {FixedControl::MainStick, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::TriggerPress},
        {FixedControl::LTrigger, PromptContext::PortMenu, PromptGesture::Press, PromptVariant::TriggerPress},
    };
    for (const auto& request : unsupported) {
        const auto answer = resolve_ps4_prompt(request, custom, allIcons);
        assert(answer.status == PromptStatus::Unresolved && !answer.icon && answer.name.empty());
        assert(!answer.reason.empty() && answer.generation == 17);
    }
    auto invalid = custom;
    invalid.config.bindings.fill(ControlTarget::Cross);
    assert(resolve_ps4_prompt({GameAction::A}, invalid).status == PromptStatus::Unresolved);
    invalid.config.bindings[0] = static_cast<ControlTarget>(99);
    assert(resolve_ps4_prompt({GameAction::A}, invalid).status == PromptStatus::Unresolved);
}
