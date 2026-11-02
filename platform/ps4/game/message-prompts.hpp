#pragma once
// Adapter for The Wind Waker's message control tags and their retained button
// pictures: fopMsgM_outFontSet/Draw/Draw2 and dDlst_2DOutFont_c::iconset. These
// are BTI pictures, not font glyphs. Picture numbers index fopMsgM_buttonTex
// after the game's own aliasing (flashing A 0x17 becomes 0x14, for example).
#include "pswaker/message-pictures.h"
#include "prompt-textures.hpp"
#include <optional>

struct MessageIconPlan {
    // Native: not a control (arrow, heart, note, starburst); the game's picture stays.
    // Prompt: show `picture`, plus `partner` as texture 0 for animated sticks.
    // Hidden: unresolved control; show nothing and report result.reason.
    enum class Kind { Native, Prompt, Hidden };
    Kind kind = Kind::Native;
    PromptResult result;
    PromptArtKey picture;
    std::optional<PromptArtKey> partner;
    // Missing artwork: picture.icon's compact accurate text tile instead.
    bool label = false;
};
// quarterTurns: the picture's clockwise quarter turns. Stick animation turns
// a tilted stick, so the displayed tilt follows the turn for animated tags.
MessageIconPlan plan_message_icon(uint8_t pictureNo, const AppliedControls& applied,
                                  uint8_t quarterTurns = 0, PromptIconAvailable available = nullptr);

// The encoded GX RGBA8 texture for artwork or its text tile, cached for the
// program lifetime in host memory. Null only if host memory is exhausted.
// Compatibility name for existing message consumers.
inline const void* message_prompt_texture(const PromptArtKey& key, bool label) { return prompt_texture(key, label); }

// Prompt adapter callback for pswaker_register_prompt_adapter. Rebuilds every
// retained message picture for this snapshot; later pictures use it too.
bool pswaker_refresh_message_prompts(void*, const AppliedControls& applied);

// Unresolved coverage, reported once per item and applied generation.
// Supplied by the program (console log) or the hosted check.
void pswaker_report_prompt_coverage(const char* surface, unsigned item, const char* reason);
