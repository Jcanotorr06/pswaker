#include "embedded-prompts.hpp"
#include "prompt-art.hpp"
#include <algorithm>
#include <cctype>
#include <vector>
#if defined(__ORBIS__)
#include <dolphin/types.h>
class JKRHeap;
#include "pc/game_hooks/jkr_heap.h"
#endif

void pswaker_report_prompt_coverage(const char*, unsigned, const char*);

namespace {
// There is one title proc. Its BTI is a whole instruction, not a logo atlas.
const void* owner = nullptr;
const void* source = nullptr;
std::vector<uint8_t> pixels;
std::optional<AppliedControls> snapshot;
std::optional<uint64_t> renderedGeneration;
constexpr unsigned width = 560, height = 80;
struct HostAllocation {
#if defined(__ORBIS__)
    JKRPcHostAllocScope scope;
#endif
};

bool rebuild() {
    if (!source) return true;
    if (snapshot && renderedGeneration == snapshot->generation) return true;
    std::vector<uint8_t> next(width * height * 4);
    const auto instruction = snapshot ? pswaker_title_instruction(*snapshot) :
        EmbeddedInstruction{"", PromptStatus::Unresolved, 0};
    if (instruction.status == PromptStatus::Unresolved ||
        !render_prompt_instruction(instruction.text, width, height, next)) {
        pswaker_report_prompt_coverage("embedded-title", 0x1E,
            "Instruction unresolved; stock controller artwork suppressed");
        std::fill(next.begin(), next.end(), 0);
    }
    // Raw replacement bytes are borrowed by Aurora: unregister before releasing
    // or changing them. Its registry and GX cache invalidation precede resume.
    pswaker_remove_embedded_texture(source);
    pixels = std::move(next);
    if (!pswaker_replace_embedded_texture(source, pixels, width, height)) return false;
    renderedGeneration = snapshot ? std::optional(snapshot->generation) : std::nullopt;
    return true;
}
}

EmbeddedInstruction pswaker_title_instruction(const AppliedControls& applied) {
    EmbeddedInstruction instruction{"PRESS ", PromptStatus::TextFallback, applied.generation};
    for (auto action : {GameAction::A, GameAction::B, GameAction::Start}) {
        const auto result = resolve_ps4_prompt({action, PromptContext::NativeGameMenu}, applied);
        if (result.status == PromptStatus::Unresolved) return {"", PromptStatus::Unresolved, applied.generation};
        if (action != GameAction::A) instruction.text += " / ";
        for (unsigned char c : result.name) instruction.text += char(std::toupper(c));
    }
    return instruction;
}

void pswaker_title_texture_set(const void* newOwner, const void* newSource) {
    [[maybe_unused]] HostAllocation host;
    if (owner) pswaker_title_texture_released(owner);
    owner = newOwner;
    source = newSource;
    renderedGeneration.reset();
    if (!source || !rebuild())
        pswaker_report_prompt_coverage("embedded-title", 0x1E, "Title texture registration unavailable");
}

void pswaker_title_texture_released(const void* releasedOwner) {
    if (owner != releasedOwner) return;
    [[maybe_unused]] HostAllocation host;
    if (source) pswaker_remove_embedded_texture(source);
    owner = source = nullptr;
    pixels.clear();
    renderedGeneration.reset();
}

bool pswaker_refresh_embedded_prompts(void*, const AppliedControls& applied) {
    [[maybe_unused]] HostAllocation host;
    snapshot = applied;
    return rebuild();
}
