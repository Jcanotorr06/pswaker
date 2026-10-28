#include "gfx/clear.hpp"
#include "gx/pipeline.hpp"

// Keep complete-package.py's pipeline-description contract tied to the actual
// selected renderer ABI. These assertions produce no runtime code or data.
static_assert(aurora::gfx::clear::ClearPipelineConfigVersion == 5 && sizeof(aurora::gfx::clear::PipelineConfig) == 8);
static_assert(aurora::gx::GXPipelineConfigVersion == 13 && sizeof(aurora::gx::PipelineConfig) == 2772);
