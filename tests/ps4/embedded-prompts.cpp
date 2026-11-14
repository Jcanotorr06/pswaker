#include "embedded-prompts.hpp"
#include "replacement-policy.hpp"
#include <cassert>
#include <vector>

static unsigned registrations = 0, releases = 0;
static std::vector<uint8_t> visible;
static bool rejectRegistration = false;
bool pswaker_replace_embedded_texture(const void*, std::span<const uint8_t> pixels,
                                     unsigned width, unsigned height) {
    assert(width == 560 && height == 80);
    assert(pixels.size() == width * height * 4);
    if (rejectRegistration) return false;
    visible.assign(pixels.begin(), pixels.end());
    ++registrations;
    return true;
}
void pswaker_remove_embedded_texture(const void*) {
    if (!visible.empty()) ++releases;
    visible.clear();
}
void pswaker_report_prompt_coverage(const char*, unsigned, const char*) { assert(false); }

int main() {
    AppliedControls applied{ControlsConfig::defaults(), 7};
    auto instruction = pswaker_title_instruction(applied);
    assert(instruction.text == "PRESS CROSS / CIRCLE / OPTIONS");
    assert(instruction.status == PromptStatus::TextFallback && instruction.generation == 7);
    assert(pswaker_refresh_embedded_prompts(nullptr, applied));
    int owner = 0, source = 0;
    pswaker_title_texture_set(&owner, &source);
    assert(registrations == 1);
    const auto defaults = visible;
    assert(pswaker_refresh_embedded_prompts(nullptr, applied));
    assert(registrations == 1);
    assert(applied.config.assign(GameAction::A, ControlTarget::R3));
    assert(applied.config.assign(GameAction::B, ControlTarget::L3));
    assert(applied.config.assign(GameAction::Start, ControlTarget::L1));
    ++applied.generation;
    instruction = pswaker_title_instruction(applied);
    assert(instruction.text == "PRESS R3 / L3 / L1");
    assert(pswaker_refresh_embedded_prompts(nullptr, applied));
    assert(registrations == 2 && releases == 1 && visible != defaults);
    ++applied.generation;
    rejectRegistration = true;
    assert(!pswaker_refresh_embedded_prompts(nullptr, applied));
    rejectRegistration = false;
    assert(pswaker_refresh_embedded_prompts(nullptr, applied));
    assert(registrations == 3 && releases == 2);
    pswaker_title_texture_released(&owner);
    assert(releases == 3);
    ++applied.generation;
    assert(pswaker_refresh_embedded_prompts(nullptr, applied));
    assert(registrations == 3);
    applied.config.bindings[0] = static_cast<ControlTarget>(99);
    instruction = pswaker_title_instruction(applied);
    assert(instruction.status == PromptStatus::Unresolved && instruction.text.empty());
}
