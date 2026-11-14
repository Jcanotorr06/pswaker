#pragma once
#include "prompts.hpp"
#include "pswaker/embedded-textures.h"
#include <span>

struct EmbeddedInstruction {
    std::string text;
    PromptStatus status;
    uint64_t generation;
};
EmbeddedInstruction pswaker_title_instruction(const AppliedControls& applied);
bool pswaker_refresh_embedded_prompts(void*, const AppliedControls& applied);

// Aurora boundary. Pixels are straight RGBA8 and borrowed until removal;
// removal synchronously drops the raw registration before memory is changed.
bool pswaker_replace_embedded_texture(const void* source, std::span<const uint8_t> pixels,
                                     unsigned width, unsigned height);
void pswaker_remove_embedded_texture(const void* source);
