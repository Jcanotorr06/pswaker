// Exercise the public artwork API only. No game headers, assets or GPU.
#include "prompt-art.hpp"
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>

namespace {
constexpr unsigned N = promptArtSize;
constexpr Ps4Icon allIcons[]{Ps4Icon::Cross, Ps4Icon::Circle, Ps4Icon::Square, Ps4Icon::Triangle,
    Ps4Icon::L1, Ps4Icon::R1, Ps4Icon::L3, Ps4Icon::R3, Ps4Icon::Options, Ps4Icon::LeftStick,
    Ps4Icon::RightStick, Ps4Icon::DPad, Ps4Icon::L2, Ps4Icon::R2, Ps4Icon::Touchpad};

PromptArtImage render(const PromptArtKey& key) {
    PromptArtImage image{};
    assert(render_prompt_art(key, image));
    return image;
}

unsigned alpha(const PromptArtImage& image, unsigned x, unsigned y) { return image[(y * N + x) * 4 + 3]; }

// The game turns retained pictures clockwise; reproduce that on the host.
PromptArtImage turnClockwise(const PromptArtImage& image) {
    PromptArtImage turned{};
    for (unsigned y = 0; y < N; ++y)
        for (unsigned x = 0; x < N; ++x)
            for (unsigned c = 0; c < 4; ++c)
                turned[(x * N + (N - 1 - y)) * 4 + c] = image[(y * N + x) * 4 + c];
    return turned;
}

// Bright-coverage centroid relative to the picture centre: symbols, labels and rims.
std::pair<double, double> centroid(const PromptArtImage& image) {
    double sum = 0, x = 0, y = 0;
    for (unsigned py = 0; py < N; ++py)
        for (unsigned px = 0; px < N; ++px) {
            const auto* pixel = &image[(py * N + px) * 4];
            const double a = pixel[3] * (pixel[0] + pixel[1] + pixel[2]) / (3.0 * 255 * 255);
            sum += a; x += a * px; y += a * py;
        }
    return {x / sum - (N - 1) / 2.0, y / sum - (N - 1) / 2.0};
}

void preview(const char* name, const PromptArtImage& image) {
    // Optional review output: raw straight RGBA, converted to PNG by the Python runner.
    if (const char* directory = std::getenv("PSWAKER_PROMPT_ART_PREVIEW")) {
        const auto path = std::string(directory) + "/" + name + ".rgba";
        FILE* file = std::fopen(path.c_str(), "wb");
        assert(file);
        std::fwrite(image.data(), 1, image.size(), file);
        std::fclose(file);
    }
}
}

int main() {
    std::vector<PromptArtImage> plain;
    for (const auto icon : allIcons) {
        const auto image = render({icon});
        // Readable artwork inside a transparent slot, so the game's shadow keeps its shape.
        assert(alpha(image, 0, 0) == 0 && alpha(image, N - 1, N - 1) == 0);
        assert(alpha(image, N / 2, N / 2) == 255);
        for (const auto& other : plain) assert(other != image);
        plain.push_back(image);
        preview(prompt_art_label(icon), image);
    }

    // Stick prompts keep movement, neutral and each tilt direction distinct.
    struct Tilt { PromptDirection direction; int dx, dy; const char* name; };
    const Tilt tilts[]{{PromptDirection::Left, -1, 0, "left"}, {PromptDirection::Up, 0, -1, "up"},
        {PromptDirection::Right, 1, 0, "right"}, {PromptDirection::Down, 0, 1, "down"},
        {PromptDirection::UpLeft, -1, -1, "up-left"}, {PromptDirection::DownRight, 1, 1, "down-right"}};
    for (const auto stick : {Ps4Icon::LeftStick, Ps4Icon::RightStick}) {
        const auto neutral = render({stick, PromptArtPose::Neutral});
        const auto move = render({stick, PromptArtPose::Move});
        assert(neutral != move && neutral != render({stick}));
        const auto [nx, ny] = centroid(neutral);
        for (const auto& tilt : tilts) {
            const auto upright = render({stick, PromptArtPose::Tilt, tilt.direction});
            const auto [x, y] = centroid(upright);
            assert((tilt.dx == 0 || (x - nx) * tilt.dx > 2.0) && (tilt.dy == 0 || (y - ny) * tilt.dy > 2.0));
            assert(tilt.dx != 0 || std::abs(x - nx) < 0.5);
            assert(tilt.dy != 0 || std::abs(y - ny) < 0.5);
            if (stick == Ps4Icon::LeftStick) preview((std::string("L-STICK-") + tilt.name).c_str(), upright);
            // A picture the game turns clockwise q times must look exactly like the upright one.
            for (uint8_t turns = 1; turns < 4; ++turns) {
                auto turned = render({stick, PromptArtPose::Tilt, tilt.direction, turns});
                assert(turned != upright);
                for (unsigned i = 0; i < turns; ++i) turned = turnClockwise(turned);
                assert(turned == upright);
            }
        }
        for (uint8_t turns = 1; turns < 4; ++turns) {
            auto turned = render({stick, PromptArtPose::Neutral, PromptDirection::None, turns});
            for (unsigned i = 0; i < turns; ++i) turned = turnClockwise(turned);
            assert(turned == neutral);
        }
    }

    // Partial and full trigger travel stay distinct from each other and the bare trigger.
    for (const auto trigger : {Ps4Icon::L2, Ps4Icon::R2}) {
        const auto partial = render({trigger, PromptArtPose::Partial});
        const auto full = render({trigger, PromptArtPose::Full});
        assert(partial != full && partial != render({trigger}) && full != render({trigger}));
        preview((std::string(prompt_art_label(trigger)) + "-PARTIAL").c_str(), partial);
        preview((std::string(prompt_art_label(trigger)) + "-FULL").c_str(), full);
    }

    // Keys that would misdescribe a control are refused rather than drawn.
    const PromptArtKey invalid[]{
        {Ps4Icon::Cross, PromptArtPose::Tilt, PromptDirection::Left},
        {Ps4Icon::LeftStick, PromptArtPose::Tilt},
        {Ps4Icon::LeftStick, PromptArtPose::Neutral, PromptDirection::Up},
        {Ps4Icon::LeftStick, PromptArtPose::Partial},
        {Ps4Icon::Cross, PromptArtPose::Full},
        {Ps4Icon::L2, PromptArtPose::Move},
        {Ps4Icon::LeftStick, PromptArtPose::Neutral, PromptDirection::None, 4},
        {static_cast<Ps4Icon>(99)},
    };
    for (const auto& key : invalid) {
        PromptArtImage image{};
        assert(!render_prompt_art(key, image));
    }

    // Missing artwork falls back to accurate compact PS4 text tiles.
    for (const auto icon : allIcons) {
        PromptArtImage image{};
        assert(render_prompt_label(prompt_art_label(icon), image));
        assert(alpha(image, N / 2, N / 2) == 255 && alpha(image, 0, 0) == 0);
    }
    PromptArtImage image{};
    assert(!render_prompt_label("", image));
    assert(!render_prompt_label("press a", image));
    assert(!render_prompt_label("TOO MANY WORDS HERE", image));
    assert(std::string(prompt_art_label(Ps4Icon::Options)) == "OPTIONS");
    assert(std::string(prompt_art_label(Ps4Icon::Touchpad)) == "TOUCH PAD");
}
