// Data-only ABI witness. Compile this same source with both the selected PS4
// flags and collector flags, then compare the complete named section bytes.
#include "gx/pipeline.hpp"
#include "gfx/clear.hpp"
#include <bit>
#include <cstddef>

using aurora::gx::PipelineConfig;
static_assert(std::endian::native == std::endian::little);
static_assert(sizeof(aurora::HashType) == 8);
static_assert(std::has_unique_object_representations_v<PipelineConfig>);
struct Contract {
  uint32_t schema = 1;
  uint32_t gxVersion = aurora::gx::GXPipelineConfigVersion;
  uint32_t clearVersion = aurora::gfx::clear::ClearPipelineConfigVersion;
  uint32_t gxBytes = sizeof(PipelineConfig);
  uint32_t clearBytes = sizeof(aurora::gfx::clear::PipelineConfig);
  uint32_t offsets[18] = {
    offsetof(PipelineConfig, version), offsetof(PipelineConfig, msaaSamples),
    offsetof(PipelineConfig, shaderConfig), offsetof(PipelineConfig, depthFunc),
    offsetof(PipelineConfig, cullMode), offsetof(PipelineConfig, blendMode),
    offsetof(PipelineConfig, blendFacSrc), offsetof(PipelineConfig, blendFacDst),
    offsetof(PipelineConfig, blendOp), offsetof(PipelineConfig, dstAlpha),
    offsetof(PipelineConfig, polygonOffsetBits), offsetof(PipelineConfig, polygonOffsetScaleBits),
    offsetof(PipelineConfig, polygonOffsetClampBits), offsetof(PipelineConfig, depthCompare),
    offsetof(PipelineConfig, depthUpdate), offsetof(PipelineConfig, alphaUpdate),
    offsetof(PipelineConfig, colorUpdate), sizeof(aurora::gx::ShaderConfig)};
  PipelineConfig gx{};
  aurora::gfx::clear::PipelineConfig clear{};
};
extern "C" __attribute__((section(".pswaker_pipeline_contract"), used))
const Contract pswaker_model_contract{};
