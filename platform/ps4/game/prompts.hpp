#pragma once
#include "controls-config.hpp"
#include <optional>
#include <string>
#include <variant>

enum class PromptContext { Gameplay, NativeGameMenu, PortMenu };
enum class FixedControl { MainStick, CStick, DPad, LTrigger, RTrigger,
    PortConfirm, PortCancel, PortSettings };
enum class PromptGesture { Press, Hold };
enum class PromptVariant { Button, StickMove, StickClick, Direction,
    RotateClockwise, RotateCounterclockwise, OscillateHorizontal, OscillateVertical,
    TriggerPartial, TriggerFull,
    // The trigger itself, for original instructions that make no travel distinction.
    Trigger };
enum class PromptDirection { None, Up, Down, Left, Right, UpLeft, UpRight, DownLeft, DownRight };
// Public, platform-independent identifiers. Availability is supplied by the
// presentation surface; an identifier never implies that artwork was loaded.
enum class Ps4Icon { Cross, Circle, Square, Triangle, L1, R1, L3, R3, Options,
    LeftStick, RightStick, DPad, L2, R2, Touchpad };
struct PromptRequest {
    std::variant<GameAction, FixedControl> control;
    PromptContext context = PromptContext::Gameplay;
    PromptGesture gesture = PromptGesture::Press;
    PromptVariant variant = PromptVariant::Button;
    PromptDirection direction = PromptDirection::None;
};
enum class PromptStatus { Icon, TextFallback, Unresolved };
struct PromptResult {
    PromptStatus status = PromptStatus::Unresolved;
    std::optional<Ps4Icon> icon;
    std::string name;
    uint64_t generation = 0;
    PromptGesture gesture = PromptGesture::Press;
    PromptVariant variant = PromptVariant::Button;
    PromptDirection direction = PromptDirection::None;
    std::string reason;
};
using PromptIconAvailable = bool (*)(Ps4Icon);
// Resolve each accepted alternative separately, preserving its gesture and
// variant. Never drop an unresolved alternative or replace it with a guess.
// With no artwork provider, every resolved control has accurate text fallback.
PromptResult resolve_ps4_prompt(const PromptRequest& request, const AppliedControls& applied,
                               PromptIconAvailable available = nullptr);

// Adapters register once on the game thread, with lifetime through shutdown.
// Return true only when retained presentation has been rebuilt for this whole
// snapshot. False delays resume and is retried on the next neutral sample.
// Callbacks must not register adapters or publish controls while refreshing.
using PromptRefreshCallback = bool (*)(void*, const AppliedControls&);
bool pswaker_register_prompt_adapter(void* context, PromptRefreshCallback refresh);
bool pswaker_refresh_prompts(const AppliedControls& applied);
