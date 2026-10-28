// Same GX scenes and pixel comparisons as the console diagnostic, on a host Vulkan device.
#include <aurora/aurora.h>
#include <aurora/gfx.hpp>
#include <aurora/gfx.h>
#include <aurora/event.h>
#include <dolphin/gx.h>
#include <dolphin/gx/GXAurora.h>
#include <dolphin/vi.h>
#include <dolphin/mtx.h>
#include <imgui.h>
#include "webgpu/gpu.hpp"
#include "window.hpp"
#include <array>
#include <atomic>
#include <chrono>
#include <cstdarg>
#include <cstdio>
#include <filesystem>
#include <memory>
#include <thread>

namespace {
unsigned failures;
void note(const char* format,...) {
  va_list args; va_start(args,format); std::vprintf(format,args); va_end(args);
  std::putchar('\n'); std::fflush(stdout);
}
void checkpoint(const char* name) { note("STAGE %s",name); }
bool verdict(bool pass,const char* name) {
  note("%s %s",pass ? "PASS" : "FAIL",name);
  if (!pass) ++failures;
  return pass;
}
void logger(AuroraLogLevel level,const char* module,const char* message,unsigned size) {
  note("AURORA level=%d module=%s %.*s",int(level),module,int(size),message);
  if (level>=LOG_ERROR) ++failures;
  if (level==LOG_FATAL) std::abort();
}
#include "../probe/white-readback.hpp"
#include "../probe/gx-setup.hpp"
#include "../probe/renderer-checks.hpp"
}
int main(int argc,char** argv) {
  std::filesystem::create_directories("cache");
  AuroraConfig config{};
  config.appName="PSWaker host renderer checks";
  config.userPath="."; config.cachePath="cache"; config.resourcesPath=".";
  config.desiredBackend=BACKEND_VULKAN; config.windowWidth=1280; config.windowHeight=720;
  config.msaa=1; config.maxTextureAnisotropy=1; config.blockingPipelines=true;
  config.allowCpuAdapter=true;
  config.logCallback=logger; config.logLevel=LOG_INFO;
  aurora_initialize(argc,argv,&config);
  AuroraSetViewportPolicy(AURORA_VIEWPORT_NATIVE);
  configure_gx_diagnostic(); aurora_update();
  verdict(prepare_gx_diagnostic_pipelines(),"GX-pipeline-preparation");
  verdict(renderer_checks(),"renderer-checks");
  // Repeat after deferred target recreation, with the same known-result comparisons.
  aurora::window::set_frame_buffer_scale(1.f); aurora_update();
  aurora::window::set_frame_buffer_scale(1.5f); aurora_update();
  verdict(renderer_checks(),"renderer-checks-after-recreation");
  verdict(drain_diagnostic_gpu(),"GPU-queue-drained");
  aurora_shutdown();
  note("END failures=%u",failures);
  return failures ? 1 : 0;
}
