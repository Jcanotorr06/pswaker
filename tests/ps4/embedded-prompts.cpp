#include "embedded-prompts.hpp"
#include "replacement-policy.hpp"
#include "prompt-art.hpp"
#include <algorithm>
#include <cassert>
#include <vector>

static unsigned registrations = 0, releases = 0, reports = 0;
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
void pswaker_report_prompt_coverage(const char*, unsigned, const char*) { ++reports; }

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
    assert(!pswaker_title_texture_ready(&owner));
    // A title can be created after the startup refresh. Never display the stock
    // instruction when registration fails; retry when this retained title draws.
    rejectRegistration = true;
    const auto previousReports = reports;
    pswaker_title_texture_set(&owner, &source);
    assert(!pswaker_title_texture_ready(&owner));
    assert(!pswaker_title_texture_ready(&owner));
    assert(reports == previousReports + 1 && visible.empty());
    rejectRegistration = false;
    assert(pswaker_title_texture_ready(&owner));
    assert(registrations == 4);
    int unrelatedOwner = 0;
    assert(!pswaker_title_texture_ready(&unrelatedOwner));
    pswaker_title_texture_released(&unrelatedOwner);
    assert(pswaker_title_texture_ready(&owner));
    pswaker_title_texture_released(&owner);
    ++applied.generation;
    assert(pswaker_refresh_embedded_prompts(nullptr, applied));
    assert(registrations == 4);
    // Longest three distinct permitted names still fit the original title slot.
    applied.config = ControlsConfig::defaults();
    assert(applied.config.assign(GameAction::A, ControlTarget::Triangle));
    assert(applied.config.assign(GameAction::B, ControlTarget::Options));
    assert(applied.config.assign(GameAction::Start, ControlTarget::Square));
    instruction = pswaker_title_instruction(applied);
    assert(instruction.text == "PRESS TRIANGLE / OPTIONS / SQUARE");
    std::vector<uint8_t> longest(560 * 80 * 4);
    assert(render_prompt_instruction(instruction.text, 560, 80, longest));
    for (unsigned y = 0; y < 80; ++y)
        for (unsigned x = 0; x < 560; ++x)
            if (x == 0 || x == 559 || y == 0 || y == 79)
                assert(longest[(y * 560 + x) * 4 + 3] == 0);
    applied.config.bindings[0] = static_cast<ControlTarget>(99);
    instruction = pswaker_title_instruction(applied);
    assert(instruction.status == PromptStatus::Unresolved && instruction.text.empty());
    ++applied.generation;
    assert(pswaker_refresh_embedded_prompts(nullptr, applied));
    pswaker_title_texture_set(&owner, &source);
    assert(pswaker_title_texture_ready(&owner));
    assert(std::all_of(visible.begin(), visible.end(), [](uint8_t pixel) { return pixel == 0; }));
    pswaker_title_texture_released(&owner);
}
