#include "message-prompts.hpp"
#include <array>
#include "prompt-textures.hpp"
#if defined(__ORBIS__)
#include <dolphin/types.h>
class JKRHeap;
#include "pc/game_hooks/jkr_heap.h"
#endif

namespace {
// The control each fopMsgM_buttonTex picture shows. Message tags are gameplay
// instructions; native game menus use the same applied bindings.
std::optional<PromptRequest> request_for(uint8_t pictureNo) {
    const auto stick = [](PromptVariant variant, PromptDirection direction = PromptDirection::None) {
        return PromptRequest{FixedControl::MainStick, PromptContext::Gameplay, PromptGesture::Press, variant, direction};
    };
    switch (pictureNo) {
    case 0x00: case 0x14: return PromptRequest{GameAction::A}; // 0x14: flashing A
    case 0x01: return PromptRequest{GameAction::B};
    case 0x02: return PromptRequest{FixedControl::CStick, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::StickMove};
    // Wind Waker uses GameCube L/R as buttons: a plain press, never full travel.
    case 0x03: return PromptRequest{FixedControl::LTrigger, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::TriggerPress};
    case 0x04: return PromptRequest{FixedControl::RTrigger, PromptContext::Gameplay, PromptGesture::Press, PromptVariant::TriggerPress};
    case 0x05: return PromptRequest{GameAction::X};
    case 0x06: return PromptRequest{GameAction::Y};
    case 0x07: return PromptRequest{GameAction::Z};
    case 0x08: return PromptRequest{FixedControl::DPad};
    case 0x09: return stick(PromptVariant::RotateClockwise);
    case 0x0E: return stick(PromptVariant::Direction, PromptDirection::Up);
    case 0x0F: return stick(PromptVariant::Direction, PromptDirection::Down);
    case 0x10: return stick(PromptVariant::Direction, PromptDirection::Left);
    case 0x11: return stick(PromptVariant::Direction, PromptDirection::Right);
    case 0x12: return stick(PromptVariant::OscillateVertical);
    case 0x13: return stick(PromptVariant::OscillateHorizontal);
    default: return std::nullopt; // Arrows 0x0A-0x0D, heart, note and starburst.
    }
}

struct Retained {
    void* picture;
    void* shadow;
    uint8_t pictureNo;
    uint8_t turns;
    std::optional<uint64_t> generation;
    PswakerPictureApply apply;
};
std::array<Retained, 256> retained;
unsigned retainedCount = 0;
// The applied controls this surface last refreshed to; new pictures use it too.
std::optional<AppliedControls> snapshot;
std::optional<uint64_t> reportedGeneration;
std::array<bool, 256> reported{};
bool registryFullReported = false;

std::optional<uint64_t> snapshotGeneration() {
    return snapshot ? std::optional(snapshot->generation) : std::nullopt;
}

// Game-hook allocations (resolver text) use host memory, never the game's current heap.
struct HostAllocation {
#if defined(__ORBIS__)
    JKRPcHostAllocScope scope;
#endif
};

void report(uint8_t pictureNo, const char* reason) {
    const std::optional<uint64_t> generation = snapshotGeneration();
    if (reportedGeneration != generation) {
        reported.fill(false);
        reportedGeneration = generation;
    }
    if (reported[pictureNo]) return;
    reported[pictureNo] = true;
    pswaker_report_prompt_coverage("message-picture", pictureNo, reason);
}

void show(Retained& entry) {
    const void* image = blank_prompt_texture();
    const void* partner = blank_prompt_texture();
    if (!snapshot) {
        report(entry.pictureNo, "No applied controls snapshot has been published");
    } else {
        // Every icon this surface uses has artwork; without texture memory the
        // picture is hidden and reported rather than left as GameCube art.
        const auto plan = plan_message_icon(entry.pictureNo, *snapshot, entry.turns);
        if (plan.kind == MessageIconPlan::Kind::Hidden) {
            report(entry.pictureNo, plan.result.reason.c_str());
        } else {
            const void* picture = prompt_texture(plan.picture, plan.label);
            const void* partnerTexture = plan.partner ? prompt_texture(*plan.partner, plan.label) : nullptr;
            if (picture && (partnerTexture || !plan.partner)) {
                image = picture;
                partner = partnerTexture;
            } else {
                report(entry.pictureNo, "Prompt texture memory unavailable");
            }
        }
    }
    entry.generation = snapshotGeneration();
    entry.apply(entry.picture, entry.shadow, image, partner);
}

Retained* find(void* picture) {
    for (unsigned i = 0; i < retainedCount; ++i)
        if (retained[i].picture == picture) return &retained[i];
    return nullptr;
}
void erase(unsigned index) { retained[index] = retained[--retainedCount]; }
}

MessageIconPlan plan_message_icon(uint8_t pictureNo, const AppliedControls& applied,
                                  uint8_t quarterTurns, PromptIconAvailable available) {
    MessageIconPlan plan;
    const auto request = request_for(pictureNo);
    if (!request) return plan;
    const uint8_t turns = quarterTurns % 4;
    plan.result = resolve_ps4_prompt(*request, applied, [](Ps4Icon) { return true; });
    if (plan.result.status == PromptStatus::Unresolved) {
        plan.kind = MessageIconPlan::Kind::Hidden;
        return plan;
    }
    const Ps4Icon icon = *plan.result.icon;
    if (available && !available(icon)) {
        plan.result = resolve_ps4_prompt(*request, applied, available);
        plan.label = true;
    }
    plan.kind = MessageIconPlan::Kind::Prompt;
    plan.picture = {icon, PromptArtPose::Plain, PromptDirection::None, turns};
    switch (request->variant) {
    case PromptVariant::StickMove:
        plan.picture.pose = PromptArtPose::Move;
        break;
    case PromptVariant::Direction:
    case PromptVariant::RotateClockwise:
    case PromptVariant::OscillateHorizontal:
    case PromptVariant::OscillateVertical: {
        // The game crossfades a tilted stick with texture 0 and turns the
        // picture clockwise from its left-tilted base for animated tags.
        constexpr PromptDirection turned[]{PromptDirection::Left, PromptDirection::Up,
            PromptDirection::Right, PromptDirection::Down};
        const auto shown = request->variant == PromptVariant::Direction ? request->direction : turned[turns];
        plan.picture.pose = PromptArtPose::Tilt;
        plan.picture.tilt = shown;
        plan.partner = PromptArtKey{icon, PromptArtPose::Neutral, PromptDirection::None, turns};
        break;
    }
    default:
        break;
    }
    if (plan.label) {
        plan.picture = {icon, PromptArtPose::Plain, PromptDirection::None, turns};
        if (plan.partner) plan.partner = plan.picture;
    }
    return plan;
}

bool pswaker_refresh_message_prompts(void*, const AppliedControls& applied) {
    [[maybe_unused]] HostAllocation host;
    snapshot = applied;
    for (unsigned i = 0; i < retainedCount; ++i)
        if (retained[i].generation != applied.generation) show(retained[i]);
    return true;
}

bool pswaker_message_picture_set(void* picture, void* shadow, uint8_t pictureNo, uint8_t quarterTurns,
                                 PswakerPictureApply apply) {
    [[maybe_unused]] HostAllocation host;
    Retained* entry = find(picture);
    if (!request_for(pictureNo)) {
        if (entry) erase(static_cast<unsigned>(entry - retained.data()));
        return false;
    }
    Retained unretained{};
    if (!entry && retainedCount < retained.size()) entry = &retained[retainedCount++];
    if (!entry) {
        // Still shown correctly now, but a later Apply could not rebuild it.
        if (!registryFullReported) pswaker_report_prompt_coverage("message-picture-registry", 0, "Retained picture registry full");
        registryFullReported = true;
        entry = &unretained;
    }
    *entry = {picture, shadow, pictureNo, static_cast<uint8_t>(quarterTurns % 4), std::nullopt, apply};
    show(*entry);
    return true;
}

void pswaker_message_picture_turned(void* picture, uint8_t quarterTurns) {
    Retained* entry = find(picture);
    if (!entry) return;
    const uint8_t turns = quarterTurns % 4;
    const auto generation = snapshotGeneration();
    if (entry->turns == turns && entry->generation == generation) return;
    [[maybe_unused]] HostAllocation host;
    entry->turns = turns;
    show(*entry);
}

void pswaker_message_picture_released(void* picture) {
    for (unsigned i = retainedCount; i-- > 0;)
        if (retained[i].picture == picture || retained[i].shadow == picture) erase(i);
}
