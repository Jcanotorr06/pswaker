// Throwaway repro: the pinned Aurora GX/frame/readback path on Linux Vulkan.
// Software Vulkan cannot establish PS4 behavior.
#include <aurora/aurora.h>
#include <aurora/event.h>
#include <aurora/gfx.hpp>
#include <aurora/gfx.h>
#include <dolphin/gx.h>
#include <dolphin/gx/GXAurora.h>
#include <dolphin/mtx.h>
#include <dolphin/vi.h>
#include <SDL3/SDL.h>
#include "webgpu/gpu.hpp"
#include "window.hpp"
#include <array>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <thread>
#include <string_view>
#include <string>
#include <cstdarg>
#include <mutex>
#include <imgui.h>


void logger(AuroraLogLevel level,const char* module,const char* message,unsigned len) {
  std::fprintf(stderr,"AURORA level=%d module=%s %.*s\n",int(level),module,int(len),message);
  if (level==LOG_FATAL) std::abort();
}
std::mutex note_mutex;
unsigned failures=0;
void note(const char* format,...) {
  std::lock_guard lock(note_mutex);
  va_list args; va_start(args,format); std::vprintf(format,args); va_end(args);
  std::putchar('\n');
}
void checkpoint(const char* name) { note("STAGE %s",name); }
bool verdict(bool pass,const char* name) {
  note("%s %s",pass ? "PASS" : "FAIL",name);
  if (!pass) ++failures;
  return pass;
}
#include "../probe/gx-setup.hpp"
#include "../probe/white-readback.hpp"
int main(int argc,char** argv) {
  setvbuf(stdout,nullptr,_IONBF,0);
  const std::string_view variant=argc>1 ? argv[1] : "baseline";
  const bool drain=variant=="drain";
  const bool corrected=variant=="corrected";
  std::printf("VARIANT %.*s\n",int(variant.size()),variant.data());
  AuroraConfig c{};
  c.appName="Throwaway Aurora geometry reproduction";
  const char* data_path=std::getenv("PSWAKER_REPRO_DATA");
  if (!data_path) return 2;
  const std::string cache_path=std::string(data_path)+"/cache";
  c.userPath=data_path; c.cachePath=cache_path.c_str();
  c.resourcesPath="."; c.desiredBackend=BACKEND_VULKAN; c.windowWidth=1920; c.windowHeight=1080;
  c.vsync=false; c.msaa=1; c.maxTextureAnisotropy=1; c.logCallback=logger; c.logLevel=LOG_INFO;
  c.allowCpuAdapter=true; // Linux reproduction only; never enabled in the console diagnostic.
  aurora_initialize(argc,argv,&c);
  AuroraSetViewportPolicy(AURORA_VIEWPORT_NATIVE);
  if (corrected) configure_gx_diagnostic();
  else aurora::window::set_frame_buffer_scale(variant=="scale" ? 1.5f : 2.f/3.f);
  aurora_update();
  u32 width=0,height=0; AuroraGetRenderSize(&width,&height);
  const bool sizing=width==1280 && height==720;
  std::printf("%s internal-size actual=%ux%u expected=1280x720\n",sizing ? "PASS" : "FAIL",width,height);
  if (corrected && !verdict(prepare_gx_diagnostic_pipelines(),"GX-pipeline-preparation")) return 1;
  if (variant=="initialize" || variant=="initialize-repeat" || variant=="alpha") GXInit(nullptr,0);
  if (variant=="alpha") GXSetPixelFmt(GX_PF_RGBA6_Z24,GX_ZC_LINEAR);
  const unsigned frame_count=variant=="repeat" || variant=="initialize-repeat" || variant=="alpha" || corrected ? 30 : 1;
  bool graphics=false;
  for (unsigned attempt=0;attempt<frame_count;++attempt) {
    aurora_update();
    if (!aurora_begin_frame()) continue;
    triangle(true);
    if (drain) AuroraGXSync();
    aurora::gfx::ResolvedTargets efb{},offscreen{};
    const bool resolved=aurora::gfx::resolve_pass({},efb);
    if (corrected) verdict(efb.width==1280 && efb.height==720,"allocated-EFB-render-size");
    const bool created=aurora::gfx::create_pass(32,32);
    if (created) { triangle(true,32,32); if (drain) AuroraGXSync(); }
    const bool offresolved=created && aurora::gfx::resolve_pass({},offscreen);
    triangle();
    aurora_end_frame(); aurora::gfx::synchronize();
    const bool efb_white=white_snapshot(efb.colorTexture,"Aurora-EFB-known-white-readback");
    const bool off_white=white_snapshot(offscreen.colorTexture,"Aurora-offscreen-known-white-readback");
    graphics=resolved && offresolved && efb_white && off_white;
    std::printf("FRAME %u graphics=%d\n",attempt,graphics);
    if (frame_count>1) std::this_thread::sleep_for(std::chrono::milliseconds(20));
  }
  verdict(drain_diagnostic_gpu(),"GPU-queue-drained");
  aurora_shutdown();
  std::printf("RESULT sizing=%d graphics=%d\n",sizing,graphics);
  return sizing && graphics && !failures ? 0 : 1;
}
