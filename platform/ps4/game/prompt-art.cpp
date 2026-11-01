#include "prompt-art.hpp"
#include <algorithm>
#include <cmath>

namespace {
constexpr int N = promptArtSize;
struct Color { float r, g, b; };
constexpr Color well{0.09f, 0.10f, 0.12f}, shell{0.15f, 0.16f, 0.19f}, rim{0.90f, 0.91f, 0.94f},
    white{1.0f, 1.0f, 1.0f}, motion{1.0f, 0.82f, 0.30f};
// Conventional PlayStation face-symbol hues, drawn as original shapes.
constexpr Color crossBlue{0.49f, 0.70f, 0.92f}, circleRed{1.0f, 0.42f, 0.42f},
    squarePink{0.92f, 0.62f, 0.83f}, triangleGreen{0.26f, 0.86f, 0.64f};

struct Vec { float x, y; };
Vec operator+(Vec a, Vec b) { return {a.x + b.x, a.y + b.y}; }
Vec operator-(Vec a, Vec b) { return {a.x - b.x, a.y - b.y}; }
Vec operator*(Vec a, float s) { return {a.x * s, a.y * s}; }
float dot(Vec a, Vec b) { return a.x * b.x + a.y * b.y; }
float length(Vec v) { return std::sqrt(dot(v, v)); }
constexpr Vec centre{N / 2.0f, N / 2.0f};

// Signed distances in pixels, negative inside.
auto circle(Vec c, float r) { return [=](Vec p) { return length(p - c) - r; }; }
auto ring(Vec c, float r, float w) { return [=](Vec p) { return std::abs(length(p - c) - r) - w / 2; }; }
auto box(Vec c, Vec half, float radius) {
    return [=](Vec p) {
        const Vec q{std::abs(p.x - c.x) - half.x + radius, std::abs(p.y - c.y) - half.y + radius};
        return length({std::max(q.x, 0.0f), std::max(q.y, 0.0f)}) + std::min(std::max(q.x, q.y), 0.0f) - radius;
    };
}
auto segment(Vec a, Vec b, float w) {
    return [=](Vec p) {
        const Vec pa = p - a, ba = b - a;
        const float h = std::clamp(dot(pa, ba) / dot(ba, ba), 0.0f, 1.0f);
        return length(pa - ba * h) - w / 2;
    };
}
template <class A, class B> auto either(A a, B b) { return [=](Vec p) { return std::min(a(p), b(p)); }; }
template <class D> auto inset(D d, float by) { return [=](Vec p) { return d(p) + by; }; }

class Canvas {
public:
    explicit Canvas(PromptArtImage& out) : out(out) { out.fill(0); }
    template <class Distance> void fill(Distance distance, Color color) {
        for (int y = 0; y < N; ++y)
            for (int x = 0; x < N; ++x)
                blend(x, y, color, std::clamp(0.5f - distance(Vec{x + 0.5f, y + 0.5f}), 0.0f, 1.0f));
    }
    // A control body: light rim around a dark face.
    template <class Distance> void body(Distance distance, Color face = shell) {
        fill(distance, rim);
        fill(inset(distance, 2.5f), face);
    }
    void coverage(const std::array<float, N * N>& cover, Color color) {
        for (int i = 0; i < N * N; ++i) blend(i % N, i / N, color, std::min(cover[i], 1.0f));
    }

private:
    void blend(int x, int y, Color c, float a) {
        if (a <= 0) return;
        auto* pixel = &out[(y * N + x) * 4];
        const float below = pixel[3] / 255.0f, total = a + below * (1 - a);
        const float source[]{c.r, c.g, c.b};
        for (int i = 0; i < 3; ++i)
            pixel[i] = static_cast<uint8_t>(std::lround((source[i] * a + pixel[i] / 255.0f * below * (1 - a)) / total * 255));
        pixel[3] = static_cast<uint8_t>(std::lround(total * 255));
    }
    PromptArtImage& out;
};

// 5x7 glyphs, most significant of five bits on the left.
struct Glyph { char c; uint8_t rows[7]; };
constexpr Glyph glyphs[]{
    {'A', {14, 17, 17, 31, 17, 17, 17}}, {'C', {14, 17, 16, 16, 16, 17, 14}},
    {'D', {30, 17, 17, 17, 17, 17, 30}}, {'E', {31, 16, 16, 30, 16, 16, 31}},
    {'G', {14, 17, 16, 23, 17, 17, 15}}, {'H', {17, 17, 17, 31, 17, 17, 17}},
    {'I', {14, 4, 4, 4, 4, 4, 14}}, {'K', {17, 18, 20, 24, 20, 18, 17}},
    {'L', {16, 16, 16, 16, 16, 16, 31}}, {'N', {17, 25, 21, 19, 17, 17, 17}},
    {'O', {14, 17, 17, 17, 17, 17, 14}}, {'P', {30, 17, 17, 30, 16, 16, 16}},
    {'Q', {14, 17, 17, 17, 21, 18, 13}}, {'R', {30, 17, 17, 30, 20, 18, 17}},
    {'S', {15, 16, 16, 14, 1, 1, 30}}, {'T', {31, 4, 4, 4, 4, 4, 4}},
    {'U', {17, 17, 17, 17, 17, 17, 14}}, {'1', {4, 12, 4, 4, 4, 4, 14}},
    {'2', {14, 17, 1, 2, 4, 8, 31}}, {'3', {30, 1, 1, 14, 1, 1, 30}},
    {'-', {0, 0, 0, 31, 0, 0, 0}}, {' ', {0, 0, 0, 0, 0, 0, 0}},
};
const Glyph* glyph(char c) {
    for (const auto& g : glyphs) if (g.c == c) return &g;
    return nullptr;
}

// One line, or two lines split at the only space. Nothing longer is compact.
bool split(std::string_view label, std::string_view lines[2], unsigned& count) {
    if (label.empty() || label.front() == ' ' || label.back() == ' ') return false;
    if (!std::all_of(label.begin(), label.end(), [](char c) { return glyph(c) != nullptr; })) return false;
    const auto space = label.find(' ');
    if (space != std::string_view::npos && label.find(' ', space + 1) != std::string_view::npos) return false;
    lines[0] = label;
    count = 1;
    if (space != std::string_view::npos) {
        lines[0] = label.substr(0, space);
        lines[1] = label.substr(space + 1);
        count = 2;
    }
    return true;
}

// Draw centred compact text in a box. Two words wrap when that reads larger;
// glyphs may be up to 1.8x taller than wide so long labels stay legible.
void text(Canvas& canvas, std::string_view label, Vec c, Vec size, float maxScale, Color color) {
    std::string_view words[2];
    unsigned count = 0;
    if (!split(label, words, count)) return;
    const auto width = [](std::string_view line) { return 6.0f * line.size() - 1; };
    std::string_view lines[2]{label};
    unsigned lineCount = 1;
    float scale = std::min({size.x / width(label), size.y / 7.0f, maxScale});
    if (count == 2) {
        const float wrapped = std::min({size.x / std::max(width(words[0]), width(words[1])), size.y / 16.0f, maxScale});
        if (wrapped > scale * 1.15f) {
            lines[0] = words[0];
            lines[1] = words[1];
            lineCount = 2;
            scale = wrapped;
        }
    }
    const float units = lineCount * 7.0f + (lineCount - 1) * 2.0f;
    const float sx = scale, sy = std::min(size.y / units, scale * 1.8f);
    std::array<float, N * N> cover{};
    for (unsigned line = 0; line < lineCount; ++line) {
        const float left = c.x - width(lines[line]) * sx / 2;
        const float top = c.y - units * sy / 2 + line * 9.0f * sy;
        for (unsigned i = 0; i < lines[line].size(); ++i) {
            const auto* g = glyph(lines[line][i]);
            for (int row = 0; row < 7; ++row)
                for (int column = 0; column < 5; ++column) {
                    if (!(g->rows[row] & (16 >> column))) continue;
                    // Exact box-filtered coverage of one glyph cell.
                    const float x0 = left + (i * 6 + column) * sx, x1 = x0 + sx;
                    const float y0 = top + row * sy, y1 = y0 + sy;
                    for (int y = std::max(0, static_cast<int>(y0)); y < std::min(N, static_cast<int>(std::ceil(y1))); ++y)
                        for (int x = std::max(0, static_cast<int>(x0)); x < std::min(N, static_cast<int>(std::ceil(x1))); ++x)
                            cover[y * N + x] += std::max(0.0f, std::min(x + 1.0f, x1) - std::max<float>(x, x0)) *
                                                std::max(0.0f, std::min(y + 1.0f, y1) - std::max<float>(y, y0));
                }
        }
    }
    canvas.coverage(cover, color);
}

Vec unit(PromptDirection direction) {
    constexpr float d = 0.70710678f;
    constexpr Vec units[]{{0, 0}, {0, -1}, {0, 1}, {-1, 0}, {1, 0}, {-d, -d}, {d, -d}, {-d, d}, {d, d}};
    return units[static_cast<unsigned>(direction)];
}
void chevron(Canvas& canvas, Vec u, float tip, float depth, float spread, Color color) {
    const Vec perpendicular{-u.y, u.x};
    const Vec point = centre + u * tip, back = centre + u * (tip - depth);
    canvas.fill(either(segment(back + perpendicular * spread, point, 3.5f),
        segment(back - perpendicular * spread, point, 3.5f)), color);
}

void face(Canvas& canvas, Ps4Icon icon) {
    canvas.fill(circle(centre, 30), rim);
    canvas.fill(circle(centre, 27.5f), shell);
    switch (icon) {
    case Ps4Icon::Cross:
        canvas.fill(either(segment(centre + Vec{-10, -10}, centre + Vec{10, 10}, 5.5f),
            segment(centre + Vec{10, -10}, centre + Vec{-10, 10}, 5.5f)), crossBlue);
        break;
    case Ps4Icon::Circle: canvas.fill(ring(centre, 11, 5.5f), circleRed); break;
    case Ps4Icon::Square: canvas.fill(inset([](Vec p) { return std::abs(box(centre, {11, 11}, 1.5f)(p)); }, -2.75f), squarePink); break;
    default: {
        const Vec top{32, 19}, left{20, 40}, right{44, 40};
        canvas.fill(either(either(segment(top, left, 5), segment(left, right, 5)), segment(right, top, 5)), triangleGreen);
    }
    }
}

void stick(Canvas& canvas, const char* label, PromptArtPose pose, PromptDirection tilt) {
    canvas.body(circle(centre, 24), well);
    const Vec cap = centre + (pose == PromptArtPose::Tilt ? unit(tilt) * 6 : Vec{0, 0});
    canvas.body(circle(cap, 17.5f));
    text(canvas, label, cap, {24, 19}, 3, white);
    if (pose == PromptArtPose::Tilt) chevron(canvas, unit(tilt), 31, 6, 6, motion);
    if (pose == PromptArtPose::Move || pose == PromptArtPose::Plain)
        for (const auto direction : {PromptDirection::Up, PromptDirection::Down, PromptDirection::Left, PromptDirection::Right})
            chevron(canvas, unit(direction), 31, 5, 5, motion);
}

void trigger(Canvas& canvas, const char* label, PromptArtPose pose) {
    canvas.body(box(centre, {26, 28}, 12));
    if (pose == PromptArtPose::Plain) {
        text(canvas, label, centre, {38, 30}, 4, white);
        return;
    }
    // A travel gauge: half filled below 90% travel, completely filled at 90% or more.
    text(canvas, label, {32, 25}, {38, 20}, 4, white);
    canvas.body(box({32, 46}, {17, 5}, 3), well);
    if (pose == PromptArtPose::Partial) canvas.fill(box({24.75f, 46}, {7.25f, 2.5f}, 1), motion);
    else canvas.fill(box({32, 46}, {14.5f, 2.5f}, 1), motion);
}

bool valid(const PromptArtKey& key) {
    if (static_cast<unsigned>(key.icon) > static_cast<unsigned>(Ps4Icon::Touchpad) || key.quarterTurns > 3 ||
        static_cast<unsigned>(key.tilt) > static_cast<unsigned>(PromptDirection::DownRight))
        return false;
    const bool isStick = key.icon == Ps4Icon::LeftStick || key.icon == Ps4Icon::RightStick;
    const bool isTrigger = key.icon == Ps4Icon::L2 || key.icon == Ps4Icon::R2;
    switch (key.pose) {
    case PromptArtPose::Plain: return key.tilt == PromptDirection::None;
    case PromptArtPose::Neutral:
    case PromptArtPose::Move: return isStick && key.tilt == PromptDirection::None;
    case PromptArtPose::Tilt: return isStick && key.tilt != PromptDirection::None;
    case PromptArtPose::Partial:
    case PromptArtPose::Full: return isTrigger && key.tilt == PromptDirection::None;
    }
    return false;
}

void turnCounterclockwise(PromptArtImage& image) {
    const auto source = image;
    for (int y = 0; y < N; ++y)
        for (int x = 0; x < N; ++x)
            for (int c = 0; c < 4; ++c)
                image[((N - 1 - x) * N + y) * 4 + c] = source[(y * N + x) * 4 + c];
}
}

const char* prompt_art_label(Ps4Icon icon) {
    constexpr const char* labels[]{"CROSS", "CIRCLE", "SQUARE", "TRIANGLE", "L1", "R1", "L3", "R3",
        "OPTIONS", "L STICK", "R STICK", "D-PAD", "L2", "R2", "TOUCH PAD"};
    const auto index = static_cast<unsigned>(icon);
    return index < std::size(labels) ? labels[index] : "";
}

bool render_prompt_art(const PromptArtKey& key, PromptArtImage& out) {
    if (!valid(key)) return false;
    Canvas canvas(out);
    switch (key.icon) {
    case Ps4Icon::Cross: case Ps4Icon::Circle: case Ps4Icon::Square: case Ps4Icon::Triangle:
        face(canvas, key.icon);
        break;
    case Ps4Icon::L1: case Ps4Icon::R1:
        canvas.body(box(centre, {29, 18}, 8));
        text(canvas, prompt_art_label(key.icon), centre, {44, 24}, 4, white);
        break;
    case Ps4Icon::L3: case Ps4Icon::R3:
        stick(canvas, prompt_art_label(key.icon), PromptArtPose::Neutral, PromptDirection::None);
        break;
    case Ps4Icon::LeftStick: case Ps4Icon::RightStick:
        stick(canvas, key.icon == Ps4Icon::LeftStick ? "L" : "R", key.pose, key.tilt);
        break;
    case Ps4Icon::L2: case Ps4Icon::R2:
        trigger(canvas, prompt_art_label(key.icon), key.pose);
        break;
    case Ps4Icon::Options:
        canvas.body(box(centre, {30, 13}, 13));
        text(canvas, "OPTIONS", centre, {48, 16}, 3, white);
        break;
    case Ps4Icon::Touchpad:
        canvas.body(box(centre, {30, 20}, 6));
        text(canvas, "TOUCH PAD", centre, {46, 30}, 3, white);
        break;
    case Ps4Icon::DPad:
        canvas.body(either(box(centre, {9.5f, 28}, 3), box(centre, {28, 9.5f}, 3)));
        for (const auto direction : {PromptDirection::Up, PromptDirection::Down, PromptDirection::Left, PromptDirection::Right})
            chevron(canvas, unit(direction), 24, 5, 5, rim);
        break;
    }
    for (unsigned turn = 0; turn < key.quarterTurns; ++turn) turnCounterclockwise(out);
    return true;
}

bool render_prompt_label(std::string_view label, PromptArtImage& out, uint8_t quarterTurns) {
    std::string_view words[2];
    unsigned count = 0;
    if (!split(label, words, count) || quarterTurns > 3) return false;
    Canvas canvas(out);
    canvas.body(box(centre, {30, 22}, 7));
    text(canvas, label, centre, {50, 36}, 3, white);
    for (unsigned turn = 0; turn < quarterTurns; ++turn) turnCounterclockwise(out);
    return true;
}
