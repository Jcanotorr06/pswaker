// Exercise the message picture adapter through its public plan, picture and
// refresh calls. Synthetic picture handles stand in for J2DPicture objects.
#include "message-prompts.hpp"
#include <cassert>
#include <cstring>
#include <string>
#include <vector>

namespace {
struct Applied { void* picture; void* shadow; const void* image; const void* partner; };
std::vector<Applied> applied;
std::vector<std::string> reports;
void record(void* picture, void* shadow, const void* image, const void* partner) {
    applied.push_back({picture, shadow, image, partner});
}
bool noArt(Ps4Icon) { return false; }

// Independent GX RGBA8 decoder: 4x4 tiles, 32 bytes of AR pairs then 32 of GB.
PromptArtImage decode(const void* texture) {
    const auto* bytes = static_cast<const uint8_t*>(texture);
    assert(bytes[0] == 6); // GX_TF_RGBA8
    assert((bytes[2] << 8 | bytes[3]) == promptArtSize && (bytes[4] << 8 | bytes[5]) == promptArtSize);
    const uint32_t offset = bytes[0x1C] << 24 | bytes[0x1D] << 16 | bytes[0x1E] << 8 | bytes[0x1F];
    const uint8_t* data = bytes + offset;
    PromptArtImage image{};
    for (unsigned ty = 0; ty < promptArtSize / 4; ++ty)
        for (unsigned tx = 0; tx < promptArtSize / 4; ++tx) {
            const uint8_t* tile = data + (ty * (promptArtSize / 4) + tx) * 64;
            for (unsigned i = 0; i < 16; ++i) {
                auto* pixel = &image[((ty * 4 + i / 4) * promptArtSize + tx * 4 + i % 4) * 4];
                pixel[3] = tile[i * 2];
                pixel[0] = tile[i * 2 + 1];
                pixel[1] = tile[32 + i * 2];
                pixel[2] = tile[32 + i * 2 + 1];
            }
        }
    return image;
}
PromptArtImage art(PromptArtKey key) {
    PromptArtImage image{};
    assert(render_prompt_art(key, image));
    return image;
}
PromptArtImage label(Ps4Icon icon) {
    PromptArtImage image{};
    assert(render_prompt_label(prompt_art_label(icon), image));
    return image;
}
bool blank(const void* texture) {
    const auto image = decode(texture);
    for (unsigned i = 3; i < image.size(); i += 4) if (image[i]) return false;
    return true;
}
}

void pswaker_report_prompt_coverage(const char* surface, unsigned item, const char* reason) {
    reports.push_back(std::string(surface) + ":" + std::to_string(item) + ":" + reason);
}

int main() {
    // Before the first published snapshot, a control picture shows nothing, never GameCube art.
    int early = 0;
    assert(pswaker_message_picture_set(&early, nullptr, 0x00, 0, record));
    assert(applied.size() == 1 && blank(applied[0].image) && !reports.empty());

    const AppliedControls defaults{ControlsConfig::defaults(), 4};
    struct Case { uint8_t picture; Ps4Icon icon; PromptArtPose pose; const char* name; };
    const Case cases[]{
        {0x00, Ps4Icon::Cross, PromptArtPose::Plain, "Cross"},
        {0x01, Ps4Icon::Circle, PromptArtPose::Plain, "Circle"},
        {0x02, Ps4Icon::RightStick, PromptArtPose::Move, "Right stick movement"},
        {0x03, Ps4Icon::L2, PromptArtPose::Plain, "L2"},
        {0x04, Ps4Icon::R2, PromptArtPose::Plain, "R2"},
        {0x05, Ps4Icon::Square, PromptArtPose::Plain, "Square"},
        {0x06, Ps4Icon::Triangle, PromptArtPose::Plain, "Triangle"},
        {0x07, Ps4Icon::R1, PromptArtPose::Plain, "R1"},
        {0x08, Ps4Icon::DPad, PromptArtPose::Plain, "D-pad"},
        {0x14, Ps4Icon::Cross, PromptArtPose::Plain, "Cross"}, // flashing A
    };
    for (const auto& example : cases) {
        const auto plan = plan_message_icon(example.picture, defaults);
        assert(plan.kind == MessageIconPlan::Kind::Prompt && !plan.label && !plan.partner);
        assert(plan.picture.icon == example.icon && plan.picture.pose == example.pose);
        assert(plan.result.status == PromptStatus::Icon && plan.result.name == example.name);
        assert(plan.result.generation == 4);
    }
    // GameCube L/R act as buttons: the prompt never asks for full travel.
    assert(plan_message_icon(0x03, defaults).result.variant == PromptVariant::TriggerPress);

    // Directions and animation keep their meaning; the art counter-turns with the game's picture.
    struct Stick { uint8_t picture; uint8_t turns; PromptDirection shown; PromptVariant variant; const char* name; };
    const Stick sticks[]{
        {0x0E, 1, PromptDirection::Up, PromptVariant::Direction, "Left stick up"},
        {0x0E, 0, PromptDirection::Up, PromptVariant::Direction, "Left stick up"},
        {0x0F, 3, PromptDirection::Down, PromptVariant::Direction, "Left stick down"},
        {0x10, 0, PromptDirection::Left, PromptVariant::Direction, "Left stick left"},
        {0x11, 2, PromptDirection::Right, PromptVariant::Direction, "Left stick right"},
        {0x09, 0, PromptDirection::Left, PromptVariant::RotateClockwise, "Left stick clockwise"},
        {0x09, 1, PromptDirection::Up, PromptVariant::RotateClockwise, "Left stick clockwise"},
        {0x09, 2, PromptDirection::Right, PromptVariant::RotateClockwise, "Left stick clockwise"},
        {0x09, 3, PromptDirection::Down, PromptVariant::RotateClockwise, "Left stick clockwise"},
        {0x12, 1, PromptDirection::Up, PromptVariant::OscillateVertical, "Left stick up / down"},
        {0x12, 3, PromptDirection::Down, PromptVariant::OscillateVertical, "Left stick up / down"},
        {0x13, 0, PromptDirection::Left, PromptVariant::OscillateHorizontal, "Left stick left / right"},
        {0x13, 2, PromptDirection::Right, PromptVariant::OscillateHorizontal, "Left stick left / right"},
    };
    for (const auto& example : sticks) {
        const auto plan = plan_message_icon(example.picture, defaults, example.turns);
        assert(plan.kind == MessageIconPlan::Kind::Prompt && plan.result.name == example.name);
        assert(plan.result.variant == example.variant);
        assert(plan.picture.icon == Ps4Icon::LeftStick && plan.picture.pose == PromptArtPose::Tilt);
        assert(plan.picture.tilt == example.shown && plan.picture.quarterTurns == example.turns);
        assert(plan.partner && plan.partner->pose == PromptArtPose::Neutral && plan.partner->quarterTurns == example.turns);
    }
    // A label stays readable on a picture the game has turned.
    assert(plan_message_icon(0x00, defaults, 2).picture.quarterTurns == 2);

    // Arrows and decorations are not controls and keep the game's own pictures.
    for (const uint8_t picture : {0x0A, 0x0B, 0x0C, 0x0D, 0x15, 0x16, 0x17, 0x18, 0xFF})
        assert(plan_message_icon(picture, defaults).kind == MessageIconPlan::Kind::Native);

    // Applied remapping drives the pictures; missing artwork falls back to accurate text.
    auto remapped = defaults;
    assert(remapped.config.assign(GameAction::A, ControlTarget::R3));
    assert(remapped.config.assign(GameAction::Z, ControlTarget::L1));
    remapped.generation = 5;
    assert(plan_message_icon(0x00, remapped).picture.icon == Ps4Icon::R3);
    assert(plan_message_icon(0x14, remapped).picture.icon == Ps4Icon::R3);
    assert(plan_message_icon(0x07, remapped).picture.icon == Ps4Icon::L1);
    const auto text = plan_message_icon(0x00, remapped, 0, noArt);
    assert(text.kind == MessageIconPlan::Kind::Prompt && text.label && text.result.status == PromptStatus::TextFallback);
    assert(text.picture.icon == Ps4Icon::R3 && text.result.name == "R3");

    // An instruction that cannot be translated is hidden and reported, never guessed.
    auto invalid = defaults;
    invalid.config.bindings.fill(ControlTarget::Cross);
    const auto unresolved = plan_message_icon(0x00, invalid);
    assert(unresolved.kind == MessageIconPlan::Kind::Hidden && !unresolved.result.reason.empty());
    assert(plan_message_icon(0x08, invalid).kind == MessageIconPlan::Kind::Prompt);

    // Retained pictures: set, turn, refresh and destruction through the public calls.
    assert(pswaker_refresh_message_prompts(nullptr, defaults));
    assert(decode(applied.back().image) == art({Ps4Icon::Cross}) && applied.back().picture == &early);
    pswaker_message_picture_released(&early);
    applied.clear();
    reports.clear();
    int dialogA = 0, dialogShadowA = 0, tutorialStick = 0, tutorialShadow = 0, heart = 0, closed = 0;
    assert(pswaker_message_picture_set(&dialogA, &dialogShadowA, 0x00, 0, record));
    assert(applied.back().picture == &dialogA && applied.back().shadow == &dialogShadowA);
    assert(decode(applied.back().image) == art({Ps4Icon::Cross}) && !applied.back().partner);
    assert(pswaker_message_picture_set(&tutorialStick, &tutorialShadow, 0x0E, 1, record));
    assert(decode(applied.back().image) == art({Ps4Icon::LeftStick, PromptArtPose::Tilt, PromptDirection::Up, 1}));
    assert(decode(applied.back().partner) == art({Ps4Icon::LeftStick, PromptArtPose::Neutral, PromptDirection::None, 1}));
    assert(!pswaker_message_picture_set(&heart, nullptr, 0x15, 0, record));
    assert(pswaker_message_picture_set(&closed, nullptr, 0x01, 0, record));
    const auto count = applied.size();
    assert(count == 3);
    // Identical textures reuse one image.
    int another = 0;
    assert(pswaker_message_picture_set(&another, nullptr, 0x00, 0, record));
    assert(applied.back().image == applied[0].image);
    pswaker_message_picture_released(&another);

    // The game animating a stick picture swaps to the art for that turn; an unchanged turn does nothing.
    pswaker_message_picture_turned(&tutorialStick, 1);
    pswaker_message_picture_turned(&dialogA, 0);
    pswaker_message_picture_turned(&heart, 3);
    assert(applied.size() == count + 1);
    const auto rotating = applied.size();
    assert(pswaker_message_picture_set(&tutorialStick, &tutorialShadow, 0x09, 0, record));
    pswaker_message_picture_turned(&tutorialStick, 2);
    assert(applied.size() == rotating + 2);
    assert(decode(applied.back().image) == art({Ps4Icon::LeftStick, PromptArtPose::Tilt, PromptDirection::Right, 2}));

    // A picture reused for a decoration is no longer a control picture.
    assert(!pswaker_message_picture_set(&closed, nullptr, 0x16, 0, record));
    // A destroyed dialog picture is never touched again; destroying either half forgets the pair.
    pswaker_message_picture_released(&dialogShadowA);

    // Apply with a dialog already open rebuilds every live retained picture before resume.
    applied.clear();
    assert(pswaker_refresh_message_prompts(nullptr, remapped));
    assert(applied.size() == 1 && applied[0].picture == &tutorialStick && applied[0].shadow == &tutorialShadow);
    assert(decode(applied[0].image) == art({Ps4Icon::LeftStick, PromptArtPose::Tilt, PromptDirection::Right, 2}));
    // The same generation is not rebuilt twice, and new pictures use the refreshed snapshot.
    assert(pswaker_refresh_message_prompts(nullptr, remapped) && applied.size() == 1);
    int newDialog = 0;
    assert(pswaker_message_picture_set(&newDialog, nullptr, 0x00, 0, record));
    assert(decode(applied.back().image) == art({Ps4Icon::R3}));
    assert(reports.empty());

    // A text tile replaces missing artwork rather than leaving a GameCube picture.
    PromptArtKey key{Ps4Icon::Options};
    assert(decode(message_prompt_texture(key, true)) == label(Ps4Icon::Options));
    assert(decode(message_prompt_texture(key, false)) == art(key));

    // An unresolved control is reported against the message surface and shown as nothing.
    applied.clear();
    int broken = 0;
    assert(pswaker_refresh_message_prompts(nullptr, invalid));
    assert(pswaker_message_picture_set(&broken, nullptr, 0x00, 0, record));
    assert(blank(applied.back().image) && reports.size() == 1);
    assert(reports[0].rfind("message-picture:0:", 0) == 0);
}
