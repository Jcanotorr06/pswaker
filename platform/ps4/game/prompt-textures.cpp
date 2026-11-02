#include "prompt-textures.hpp"
#include <array>
#include <cstdlib>
#include <cstring>

namespace {
constexpr unsigned N = promptArtSize;
constexpr size_t headerSize = 0x20, textureSize = headerSize + N * N * 4;

bool same(const PromptArtKey& a, const PromptArtKey& b) {
    return a.icon == b.icon && a.pose == b.pose && a.tilt == b.tilt && a.quarterTurns == b.quarterTurns;
}

// GX_TF_RGBA8 ResTIMG: big-endian header, then 4x4 tiles of AR pairs followed by GB pairs.
void encode(const PromptArtImage& image, uint8_t* texture) {
    std::memset(texture, 0, headerSize);
    texture[0x00] = 6;      // GX_TF_RGBA8
    texture[0x01] = 1;      // alpha
    texture[0x03] = N;      // width
    texture[0x05] = N;      // height; clamp wrap at 0x06/0x07
    texture[0x14] = 1;      // GX_LINEAR minification
    texture[0x15] = 1;      // GX_LINEAR magnification
    texture[0x18] = 1;      // one image, no mipmaps
    texture[0x1F] = headerSize;
    uint8_t* tile = texture + headerSize;
    for (unsigned ty = 0; ty < N / 4; ++ty)
        for (unsigned tx = 0; tx < N / 4; ++tx, tile += 64)
            for (unsigned i = 0; i < 16; ++i) {
                const uint8_t* pixel = &image[((ty * 4 + i / 4) * N + tx * 4 + i % 4) * 4];
                tile[i * 2] = pixel[3];
                tile[i * 2 + 1] = pixel[0];
                tile[32 + i * 2] = pixel[1];
                tile[32 + i * 2 + 1] = pixel[2];
            }
}

struct Cached { PromptArtKey key; bool label; void* texture; };
std::array<Cached, 192> cache;
unsigned cachedCount = 0;

}

const void* blank_prompt_texture() {
    alignas(32) static uint8_t texture[textureSize];
    static const bool encoded = (encode(PromptArtImage{}, texture), true);
    (void)encoded;
    return texture;
}

const void* prompt_texture(const PromptArtKey& key, bool label) {
    for (unsigned i = 0; i < cachedCount; ++i)
        if (cache[i].label == label && same(cache[i].key, key)) return cache[i].texture;
    if (cachedCount == cache.size()) return nullptr;
    static PromptArtImage image;
    if (!(label ? render_prompt_label(prompt_art_label(key.icon), image, key.quarterTurns)
                : render_prompt_art(key, image)))
        return nullptr;
    // Host memory, never freed: retained pictures and the renderer keep the pointer.
    auto* texture = static_cast<uint8_t*>(std::aligned_alloc(32, textureSize));
    if (!texture) return nullptr;
    encode(image, texture);
    cache[cachedCount++] = {key, label, texture};
    return texture;
}
