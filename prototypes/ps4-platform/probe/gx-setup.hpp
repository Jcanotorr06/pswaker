// Shared by the full PS4 diagnostic and its Linux Aurora reproduction.
// Included after the Aurora/GX/SDL/C++ headers, inside the diagnostic namespace.
#include "gx-scene.hpp"
void configure_gx_diagnostic() {
  // Aurora creates the renderer/FIFO, but the application initializes GX's shadow
  // register command bytes and defaults. Without this, setters encode bad state.
  GXInit(nullptr,0);
  // The known-white comparison includes alpha. RGB8 leaves offscreen alpha at 0.
  GXSetPixelFmt(GX_PF_RGBA6_Z24,GX_ZC_LINEAR);
  VIConfigure(&GXNtsc480IntDf);
  // Aurora scales the configured VI size (640x480), then expands to the display
  // aspect. At 16:9 this yields 1280x720, independently of the 1080p surface.
  aurora::window::set_frame_buffer_scale(720.f/480.f);
}
bool prepare_gx_diagnostic_pipelines() {
  // Queue precisely the EFB/offscreen white and EFB RGB pipeline configurations.
  // Their initial asynchronous compilation is preparation, before comparisons.
  if (!aurora_begin_frame()) return false;
  triangle(true);
  aurora::gfx::ResolvedTargets first{},second{};
  const bool efb=aurora::gfx::resolve_pass({},first);
  const bool offscreen=aurora::gfx::create_pass(32,32);
  if (offscreen) triangle(true,32,32);
  const bool resolved=offscreen && aurora::gfx::resolve_pass({},second);
  triangle();
  ImGui::Begin("Disc-free diagnostic preparation");
  ImGui::Text("Preparing known diagnostic shaders. Hardware checks follow.");
  ImGui::End();
  aurora_end_frame();
  aurora::gfx::synchronize();
  const auto until=std::chrono::steady_clock::now()+std::chrono::seconds(30);
  const auto queued=[] {
    return std::atomic_ref<const uint32_t>(aurora_get_stats()->queuedPipelines).load(std::memory_order_relaxed);
  };
  while (queued()!=0 && std::chrono::steady_clock::now()<until) {
    aurora::webgpu::g_instance.ProcessEvents();
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
  return efb && resolved && queued()==0;
}
bool drain_diagnostic_gpu() {
  aurora::gfx::synchronize();
  auto done=std::make_shared<std::atomic<int>>(0);
  aurora::webgpu::g_queue.OnSubmittedWorkDone(wgpu::CallbackMode::AllowProcessEvents,
    [done](wgpu::QueueWorkDoneStatus status,wgpu::StringView) {
      done->store(status==wgpu::QueueWorkDoneStatus::Success ? 1 : -1);
    });
  const auto until=std::chrono::steady_clock::now()+std::chrono::seconds(10);
  while (*done==0 && std::chrono::steady_clock::now()<until) {
    aurora::webgpu::g_instance.ProcessEvents();
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
  aurora::webgpu::g_instance.ProcessEvents();
  return *done==1;
}
