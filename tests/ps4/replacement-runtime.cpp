// Real patched Aurora registry and GX object caches. Only GPU allocation is
// replaced; handles carry a synthetic pixel marker and have no WebGPU objects.
#include "gfx/texture_replacement.hpp"
#include "gx/texture.hpp"
#include "replacement-policy.hpp"
#include "frame-pacing.hpp"
#include <array>
#include <cassert>
#include <chrono>

extern "C" uint64_t pswaker_perf_now() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}
extern "C" void pswaker_perf_shader_wait(uint64_t) {}
extern "C" PswakerFrameTag pswaker_perf_capture() { return {}; }
extern "C" void pswaker_perf_present(PswakerFrameTag) {}
extern "C" void pswaker_perf_present_failed() {}

static bool failUploads = false;

extern "C" aurora::gfx::TextureHandle
__wrap__ZN6aurora3gfx21new_static_texture_2dEjjjjNS_8ArrayRefIhEEbPKc(
    uint32_t width, uint32_t height, uint32_t mips, uint32_t,
    aurora::ArrayRef<uint8_t> pixels, bool, const char*) noexcept {
    if (failUploads && pixels.data()[0] == 0x22) return {};
    return std::make_shared<aurora::gfx::TextureRef>(nullptr, nullptr, nullptr,
        wgpu::Extent3D{width, height, 1}, wgpu::TextureFormat::RGBA8Unorm, mips, pixels.data()[0]);
}

int main() {
    namespace tex = aurora::texture;
    namespace gx = aurora::gx::texture;
    namespace runtime = aurora::gfx::texture_replacement;
    using namespace pswaker::replacement;
    std::array<uint8_t, 64> stock{}, pack{}, prompt{}, refreshed{};
    pack.fill(0x11); prompt.fill(0x22); refreshed.fill(0x33);
    GXTexObj_ object{};
    object.data = stock.data(); object.mWidth = object.mHeight = 4;
    object.mFormat = GX_TF_RGBA8_PC; object.texObjId = 103;
    const tex::ReplacementKey pointer = tex::TexturePointerKey{stock.data()};
    const auto source = tex::parse_replacement_filename(runtime::build_texture_replacement_name(object));
    assert(source);
    const auto add = [&](tex::ReplacementKey key, const auto& pixels, int priority) {
        return tex::register_replacement(key,
            {.bytes = pixels, .width = 4, .height = 4, .gxFormat = GX_TF_RGBA8_PC}, {priority});
    };
    const auto resolve = [&] {
        // Same render-thread boundary used before retained GX bindings are read.
        gx::current_bind_generation();
        return gx::resolve_static_texture(object);
    };
    for (bool promptPointer : {false, true})
        for (bool packPointer : {false, true})
            for (bool promptFirst : {false, true}) {
                const tex::ReplacementKey promptKey = promptPointer ? pointer : tex::ReplacementKey{*source};
                const tex::ReplacementKey packKey = packPointer ? pointer : tex::ReplacementKey{*source};
                tex::ReplacementRegistration p, competing;
                if (promptFirst) p = add(promptKey, prompt, promptPriority);
                competing = add(packKey, pack, packMaximumPriority);
                if (!promptFirst) {
                    assert(resolve()->gxFormat == 0x11); // Warm real pack/object caches.
                    p = add(promptKey, prompt, promptPriority);
                }
                assert(resolve()->gxFormat == 0x22);
                assert(resolve()->gxFormat == 0x22); // Retained GX object hit.
                auto conflict = add(packKey, pack, packMaximumPriority);
                assert(resolve()->gxFormat == 0x22); // Later pack cannot replace cached prompt.
                tex::unregister_replacement(p);
                p = add(promptKey, refreshed, promptPriority);
                assert(resolve()->gxFormat == 0x33); // Applied generation rebuild.
                tex::unregister_replacement(p);
                assert(resolve()->gxFormat == 0x11);
                failUploads = true;
                p = add(promptKey, prompt, promptPriority);
                assert(!resolve()); // Missing prompt upload must never expose stock/pack instructions.
                failUploads = false;
                tex::unregister_replacement(p);
                tex::unregister_replacement(conflict);
                tex::unregister_replacement(competing);
            }
    runtime::shutdown();
    gx::shutdown();
}
