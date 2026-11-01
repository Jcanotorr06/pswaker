#pragma once
#include "prompts.hpp"
#include <array>
#include <cstdint>
#include <string_view>

// Original project-owned DualShock 4 prompt artwork, drawn by this code. No
// image files, game textures or pack artwork are read. Any prompt adapter may
// encode these pixels for its own presentation path.
inline constexpr unsigned promptArtSize = 64;
// Straight (non-premultiplied) RGBA8, row-major, top row first.
using PromptArtImage = std::array<uint8_t, promptArtSize * promptArtSize * 4>;

// Plain: the control itself. Neutral/Tilt/Move: sticks only. Partial/Full: L2/R2 travel.
enum class PromptArtPose : uint8_t { Plain, Neutral, Tilt, Move, Partial, Full };
struct PromptArtKey {
    Ps4Icon icon = Ps4Icon::Cross;
    PromptArtPose pose = PromptArtPose::Plain;
    // Tilt only: the direction the player sees once the picture is displayed.
    PromptDirection tilt = PromptDirection::None;
    // Clockwise quarter turns the presentation applies to the picture. The art
    // is pre-turned counterclockwise so labels read upright and tilts point
    // in `tilt` after that turn.
    uint8_t quarterTurns = 0;
};

// False, leaving `out` unspecified, when the pose does not describe that control.
bool render_prompt_art(const PromptArtKey& key, PromptArtImage& out);
// Compact accurate PS4 text: one or two words of A-Z, 1-3, '-' and spaces.
// quarterTurns has the same meaning as in PromptArtKey.
bool render_prompt_label(std::string_view label, PromptArtImage& out, uint8_t quarterTurns = 0);
// The compact accurate label used for missing artwork, for example "OPTIONS".
const char* prompt_art_label(Ps4Icon icon);
