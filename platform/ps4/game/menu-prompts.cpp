#include "menu-prompts.hpp"
#include "prompt-textures.hpp"
#include <array>
#include <bitset>
#if defined(__ORBIS__)
#include <dolphin/types.h>
class JKRHeap;
#include "pc/game_hooks/jkr_heap.h"
#endif

void pswaker_report_prompt_coverage(const char*, unsigned, const char*);

namespace {
struct Picture {
    void* picture = nullptr;
    PswakerMenuFamily family{};
    PswakerMenuControl control{};
    PswakerMenuApply apply = nullptr;
    std::optional<uint64_t> generation;
};
std::array<Picture, 64> pictures;
std::optional<AppliedControls> snapshot;
std::array<std::string, 2> instructions;
std::bitset<768> reported;

struct HostAllocation {
#if defined(__ORBIS__)
    JKRPcHostAllocScope scope;
#endif
};

const char* surface(PswakerMenuFamily family) {
    switch (family) {
    case PswakerMenuFamily::FileSelect: return "menu-file-select";
    case PswakerMenuFamily::SeaChart: return "menu-sea-chart";
    case PswakerMenuFamily::Window: return "menu-window";
    }
    return "menu-unknown";
}

void report(PswakerMenuFamily family, unsigned control, const char* reason) {
    const unsigned id = static_cast<unsigned>(family) * 256 + control;
    if (id < reported.size()) {
        if (reported[id]) return;
        reported[id] = true;
    }
    pswaker_report_prompt_coverage(surface(family), control, reason);
}

std::optional<PromptRequest> request(PswakerMenuControl control) {
    switch (control) {
    case PswakerMenuControl::A: return PromptRequest{GameAction::A, PromptContext::NativeGameMenu};
    case PswakerMenuControl::B: return PromptRequest{GameAction::B, PromptContext::NativeGameMenu};
    case PswakerMenuControl::L: return PromptRequest{FixedControl::LTrigger, PromptContext::NativeGameMenu,
        PromptGesture::Press, PromptVariant::TriggerPress};
    case PswakerMenuControl::R: return PromptRequest{FixedControl::RTrigger, PromptContext::NativeGameMenu,
        PromptGesture::Press, PromptVariant::TriggerPress};
    }
    return std::nullopt;
}

void show(Picture& picture) {
    const void* texture = blank_prompt_texture();
    const auto semantic = request(picture.control);
    if (!snapshot || !semantic) {
        report(picture.family, static_cast<unsigned>(picture.control),
            !snapshot ? "No applied controls snapshot has been published" : "Unknown native menu control");
    } else {
        const auto result = resolve_ps4_prompt(*semantic, *snapshot, [](Ps4Icon) { return true; });
        if (result.status == PromptStatus::Unresolved) {
            report(picture.family, static_cast<unsigned>(picture.control), result.reason.c_str());
        } else {
            texture = prompt_texture({*result.icon}, false);
            if (!texture) texture = prompt_texture({*result.icon}, true);
            if (!texture) {
                texture = blank_prompt_texture();
                report(picture.family, static_cast<unsigned>(picture.control), "Prompt texture memory unavailable");
            }
        }
    }
    picture.apply(picture.picture, texture);
    picture.generation = snapshot ? std::optional(snapshot->generation) : std::nullopt;
}

std::string alternative(GameAction first, const char* meaning) {
    const auto a = resolve_ps4_prompt({first, PromptContext::NativeGameMenu}, *snapshot);
    const auto start = resolve_ps4_prompt({GameAction::Start, PromptContext::NativeGameMenu}, *snapshot);
    if (a.status == PromptStatus::Unresolved || start.status == PromptStatus::Unresolved) {
        report(first == GameAction::A ? PswakerMenuFamily::FileSelect : PswakerMenuFamily::Window,
            0xFE, a.status == PromptStatus::Unresolved ? a.reason.c_str() : start.reason.c_str());
        return {};
    }
    return a.name + " / " + start.name + ": " + meaning;
}
}

void pswaker_menu_picture_set(void* picture, PswakerMenuFamily family,
                              PswakerMenuControl control, PswakerMenuApply apply) {
    if (!picture || !apply) return;
    [[maybe_unused]] HostAllocation host;
    Picture* free = nullptr;
    for (auto& entry : pictures) {
        if (entry.picture == picture) { free = &entry; break; }
        if (!entry.picture && !free) free = &entry;
    }
    if (!free) {
        apply(picture, blank_prompt_texture());
        report(family, static_cast<unsigned>(control), "Retained native menu registry full; picture suppressed");
        return;
    }
    *free = {picture, family, control, apply, std::nullopt};
    show(*free);
}

void pswaker_menu_picture_released(void* picture) {
    for (auto& entry : pictures)
        if (entry.picture == picture) entry = {};
}

const char* pswaker_menu_instruction(PswakerMenuInstruction instruction) {
    const auto index = static_cast<unsigned>(instruction);
    return index < instructions.size() ? instructions[index].c_str() : "";
}

void pswaker_menu_missing_picture(PswakerMenuFamily family, unsigned tag) {
    pswaker_report_prompt_coverage(surface(family), tag, "Expected native menu control picture absent or wrong pane type");
}

bool pswaker_refresh_menu_prompts(void*, const AppliedControls& applied) {
    [[maybe_unused]] HostAllocation host;
    if (!snapshot || snapshot->generation != applied.generation) reported.reset();
    snapshot = applied;
    instructions[0] = alternative(GameAction::A, "Select");
    instructions[1] = alternative(GameAction::B, "Close");
    for (auto& entry : pictures)
        if (entry.picture && entry.generation != applied.generation) show(entry);
    return true;
}
