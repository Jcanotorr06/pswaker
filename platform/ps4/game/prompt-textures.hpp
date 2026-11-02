#pragma once
#include "prompt-art.hpp"

// Shared stock-mode GX RGBA8 ResTIMG cache, owned by host memory for the program
// lifetime. No dependency on message tags, a game archive, GPU or HD loader.
const void* prompt_texture(const PromptArtKey& key, bool label);
const void* blank_prompt_texture();
