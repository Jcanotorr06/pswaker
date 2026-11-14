#include "embedded-prompts.hpp"
#include "replacement-policy.hpp"
#include <dolphin/gx.h>
#include <aurora/texture.hpp>

namespace {
std::optional<aurora::texture::ReplacementRegistration> registration;
}

bool pswaker_replace_embedded_texture(const void* source, std::span<const uint8_t> pixels,
                                     unsigned width, unsigned height) {
    // The one retained title resource is identified at load time, before J2D
    // binds it. Aurora's combined key arbitration protects it against hash packs.
    auto added = aurora::texture::register_replacement(
        aurora::texture::TexturePointerKey{source},
        {.bytes = pixels, .width = width, .height = height, .mipCount = 1,
         .gxFormat = GX_TF_RGBA8_PC, .label = "PS4 title instruction"},
        {.priority = pswaker::replacement::promptPriority});
    if (!added.id) return false;
    registration = added;
    return true;
}

void pswaker_remove_embedded_texture(const void*) {
    if (registration) aurora::texture::unregister_replacement(*registration);
    registration.reset();
}
