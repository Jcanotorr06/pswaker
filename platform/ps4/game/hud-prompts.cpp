#include "hud-prompts.hpp"
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
    PswakerHudControl control{};
    // Non-null for native action descriptions; they contain context words or
    // weapon art, while a separate layout picture names the resolved control.
    const void* description = nullptr;
    uint16_t status = 0;
    PswakerHudApply apply = nullptr;
    std::optional<uint64_t> generation;
};
// A meter has fewer than 32 control/description pictures. Never retain an
// untracked picture on overflow: hide and report it so Apply cannot leave a
// plausible but stale instruction behind.
std::array<Picture, 128> pictures;
std::optional<AppliedControls> snapshot;
// Separate domains for every native 16-bit status and 8-bit control value,
// including unknown values: coverage failures do not flood the console log.
std::bitset<256 + 65536> reported;
std::optional<uint64_t> reportedGeneration;

struct HostAllocation {
#if defined(__ORBIS__)
    JKRPcHostAllocScope scope;
#endif
};

std::optional<PromptRequest> request(PswakerHudControl control) {
    switch (control) {
    case PswakerHudControl::A: return PromptRequest{GameAction::A};
    case PswakerHudControl::B: return PromptRequest{GameAction::B};
    case PswakerHudControl::X: return PromptRequest{GameAction::X};
    case PswakerHudControl::Y: return PromptRequest{GameAction::Y};
    case PswakerHudControl::Z: return PromptRequest{GameAction::Z};
    case PswakerHudControl::Start: return PromptRequest{GameAction::Start};
    case PswakerHudControl::L: return PromptRequest{FixedControl::LTrigger, PromptContext::Gameplay,
        PromptGesture::Press, PromptVariant::TriggerPress};
    case PswakerHudControl::R: return PromptRequest{FixedControl::RTrigger, PromptContext::Gameplay,
        PromptGesture::Press, PromptVariant::TriggerPress};
    case PswakerHudControl::DPad: return PromptRequest{FixedControl::DPad};
    }
    return std::nullopt;
}

void report(const Picture& picture, const char* reason) {
    const auto generation = snapshot ? std::optional(snapshot->generation) : std::nullopt;
    if (reportedGeneration != generation) {
        reported.reset();
        reportedGeneration = generation;
    }
    const unsigned id = picture.description ? 256 + picture.status : static_cast<unsigned>(picture.control);
    if (reported[id]) return;
    reported[id] = true;
    pswaker_report_prompt_coverage(picture.description ? "hud-action-description" : "hud-layout-picture",
        picture.description ? picture.status : static_cast<unsigned>(picture.control), reason);
}

void show(Picture& picture) {
    const void* texture = blank_prompt_texture();
    const auto semantic = request(picture.control);
    if (!snapshot || !semantic) {
        report(picture, !snapshot ? "No applied controls snapshot has been published" :
            picture.description ? "Unmapped meter action-description status" : "Unknown meter control");
    } else {
        const auto result = resolve_ps4_prompt(*semantic, *snapshot, [](Ps4Icon) { return true; });
        if (result.status == PromptStatus::Unresolved) {
            report(picture, result.reason.c_str());
        } else if (picture.description) {
            texture = picture.description;
        } else {
            texture = prompt_texture({*result.icon}, false);
            // Accurate PS4 text if artwork is unavailable; never a GameCube tile.
            if (!texture) texture = prompt_texture({*result.icon}, true);
            if (!texture) {
                texture = blank_prompt_texture();
                report(picture, "Prompt texture memory unavailable");
            }
        }
    }
    picture.apply(picture.picture, texture);
    picture.generation = snapshot ? std::optional(snapshot->generation) : std::nullopt;
}

void retain(Picture picture) {
    [[maybe_unused]] HostAllocation host;
    Picture* free = nullptr;
    for (auto& entry : pictures) {
        if (entry.picture == picture.picture) { free = &entry; break; }
        if (!entry.picture && !free) free = &entry;
    }
    if (!free) {
        picture.apply(picture.picture, blank_prompt_texture());
        report(picture, "Retained HUD picture registry full; picture suppressed");
        return;
    }
    *free = picture;
    show(*free);
}
}

void pswaker_hud_picture_set(void* picture, PswakerHudControl control, PswakerHudApply apply) {
    retain({picture, control, nullptr, 0, apply, std::nullopt});
}

void pswaker_hud_description_set(void* picture, PswakerHudControl control, uint16_t status,
                                const void* texture, PswakerHudApply apply) {
    retain({picture, control, texture, status, apply, std::nullopt});
}

void pswaker_hud_picture_released(void* picture) {
    for (auto& entry : pictures)
        if (entry.picture == picture) entry = {};
}

bool pswaker_refresh_hud_prompts(void*, const AppliedControls& applied) {
    [[maybe_unused]] HostAllocation host;
    snapshot = applied;
    for (auto& entry : pictures)
        if (entry.picture && entry.generation != applied.generation) show(entry);
    return true;
}
