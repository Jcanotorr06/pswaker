// Throwaway, disc-free platform diagnostic. A build is not a hardware result.
#include <aurora/aurora.h>
#include <aurora/event.h>
#include <aurora/gfx.hpp>
#include <dolphin/gx.h>
#include <dolphin/gx/GXAurora.h>
#include <dolphin/mtx.h>
#include <SDL3/SDL.h>
#include <imgui.h>
#include "webgpu/gpu.hpp"
#include "window.hpp"
#include "native/platform.h"
#include <orbis/Pad.h>
#include <orbis/UserService.h>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdarg>
#include <cstdio>
#include <dirent.h>
#include <memory>
#include <mutex>
#include <string>
#include <sys/stat.h>
#include <thread>

#define main runtime_preflight_entry
#include "../runtime-preflight/main.cpp"
#undef main
extern "C" void ac_ps4_get_memory(uint64_t*, uint64_t*, uint64_t*);
extern "C" size_t ps4rt_heap_size();
extern "C" size_t pswaker_heap_used();
extern "C" int sceKernelAvailableFlexibleMemorySize(size_t*);
// No disc I/O exists in this diagnostic; Aurora's replacement worker has no disc work to await.
extern "C" uint64_t ps4_disc_busy_until_ns(void) { return 0; }
namespace {
FILE* evidence;
std::mutex evidence_mutex;
std::atomic<int> errors{0}, audio_errors{0};
std::atomic<uint64_t> audio_frames{0};
uint64_t audio_phase;
void note(const char* format, ...) {
  std::lock_guard lock(evidence_mutex);
  va_list args; va_start(args,format); std::vfprintf(evidence,format,args); va_end(args);
  std::fputc('\n',evidence); std::fflush(evidence);
}
void checkpoint(const char* name) {
  note("STAGE %s",name);
  if (fsync(fileno(evidence)) != 0) ++errors;
}
bool verdict(bool pass, const char* name) {
  note("%s %s",pass ? "PASS" : "FAIL",name);
  if (!pass) ++errors;
  return pass;
}
void logger(AuroraLogLevel level,const char* module,const char* message,unsigned len) {
  note("AURORA level=%d module=%s %.*s",int(level),module,int(len),message);
  if (level >= LOG_ERROR) ++errors;
  if (level == LOG_FATAL) { std::fflush(nullptr); std::abort(); }
}
void audio_callback(void*,SDL_AudioStream* stream,int needed,int) {
  std::array<int16_t,512> pcm{};
  while (needed >= 4) {
    const int count = std::min(needed/4,256);
    for (int i=0;i<count;++i) {
      const auto sample = int16_t(1500.0*std::sin(double(audio_phase++)*440.0*6.283185307179586/48000.0));
      pcm[i*2]=pcm[i*2+1]=sample;
    }
    if (!SDL_PutAudioStreamData(stream,pcm.data(),count*4)) ++audio_errors;
    audio_frames += count; needed -= count*4;
  }
}
wgpu::RenderPipeline make_pipeline(float z) {
  std::string text=R"(
struct V { @builtin(position) p: vec4f, @location(0) uv: vec2f };
@group(0) @binding(0) var image: texture_2d<f32>;
@group(0) @binding(1) var image_sampler: sampler;
@vertex fn vs(@builtin(vertex_index) index: u32) -> V {
  var points=array<vec2f,3>(vec2f(-1,-1),vec2f(3,-1),vec2f(-1,3));
  var out: V; out.p=vec4f(points[index],DEPTH,1);
  out.uv=points[index]*.5+.5; return out;
}
@fragment fn fs(v: V) -> @location(0) vec4f { return textureSample(image,image_sampler,v.uv); }
)";
  text.replace(text.find("DEPTH"),5,std::to_string(z));
  wgpu::ShaderSourceWGSL source{}; source.code=text.c_str();
  wgpu::ShaderModuleDescriptor sm{}; sm.nextInChain=&source;
  auto shader=aurora::webgpu::g_device.CreateShaderModule(&sm);
  wgpu::BlendState blend{};
  blend.color.srcFactor=wgpu::BlendFactor::SrcAlpha;
  blend.color.dstFactor=wgpu::BlendFactor::OneMinusSrcAlpha;
  blend.alpha.srcFactor=wgpu::BlendFactor::One;
  blend.alpha.dstFactor=wgpu::BlendFactor::OneMinusSrcAlpha;
  wgpu::ColorTargetState color{}; color.format=wgpu::TextureFormat::RGBA8Unorm; color.blend=&blend;
  wgpu::FragmentState fragment{};
  fragment.module=shader; fragment.entryPoint="fs"; fragment.targetCount=1; fragment.targets=&color;
  wgpu::DepthStencilState depth{};
  depth.format=wgpu::TextureFormat::Depth32Float; depth.depthWriteEnabled=true; depth.depthCompare=wgpu::CompareFunction::Less;
  wgpu::RenderPipelineDescriptor p{};
  p.vertex.module=shader; p.vertex.entryPoint="vs"; p.fragment=&fragment; p.depthStencil=&depth;
  return aurora::webgpu::g_device.CreateRenderPipeline(&p);
}
struct Targets {
  wgpu::Texture color,copy,depth,texel;
  wgpu::TextureView preview;
  wgpu::RenderPipeline near_pipeline,far_pipeline;
  wgpu::BindGroup near_group,far_group;
  void recreate() {
    checkpoint("create-targets-and-textured-depth-blend-pipelines");
    auto device=aurora::webgpu::g_device;
    wgpu::TextureDescriptor t{};
    t.size={32,32,1}; t.format=wgpu::TextureFormat::RGBA8Unorm;
    t.usage=wgpu::TextureUsage::RenderAttachment|wgpu::TextureUsage::CopySrc;
    color=device.CreateTexture(&t);
    t.usage=wgpu::TextureUsage::CopyDst|wgpu::TextureUsage::CopySrc|wgpu::TextureUsage::TextureBinding;
    copy=device.CreateTexture(&t); preview=copy.CreateView();
    t.format=wgpu::TextureFormat::Depth32Float; t.usage=wgpu::TextureUsage::RenderAttachment;
    depth=device.CreateTexture(&t);
    t.format=wgpu::TextureFormat::RGBA8Unorm; t.size={1,1,1};
    t.usage=wgpu::TextureUsage::CopyDst|wgpu::TextureUsage::TextureBinding;
    texel=device.CreateTexture(&t);
    const uint8_t red[4]={255,0,0,128};
    wgpu::TexelCopyTextureInfo destination{}; destination.texture=texel;
    wgpu::TexelCopyBufferLayout layout{}; layout.bytesPerRow=4; layout.rowsPerImage=1;
    const wgpu::Extent3D pixel{1,1,1};
    aurora::webgpu::g_queue.WriteTexture(&destination,red,sizeof red,&layout,&pixel);
    near_pipeline=make_pipeline(.2f); far_pipeline=make_pipeline(.8f);
    wgpu::SamplerDescriptor sampler_descriptor{};
    auto sampler=device.CreateSampler(&sampler_descriptor);
    wgpu::BindGroupEntry entries[2]{};
    entries[0].binding=0; entries[0].textureView=texel.CreateView();
    entries[1].binding=1; entries[1].sampler=sampler;
    wgpu::BindGroupDescriptor group{}; group.entryCount=2; group.entries=entries;
    group.layout=near_pipeline.GetBindGroupLayout(0); near_group=device.CreateBindGroup(&group);
    group.layout=far_pipeline.GetBindGroupLayout(0); far_group=device.CreateBindGroup(&group);
  }
  bool verify() {
    checkpoint("render-copy-async-readback-known-purple");
    auto device=aurora::webgpu::g_device;
    auto encoder=device.CreateCommandEncoder();
    wgpu::RenderPassColorAttachment c{};
    c.view=color.CreateView(); c.loadOp=wgpu::LoadOp::Clear; c.storeOp=wgpu::StoreOp::Store; c.clearValue={0,0,1,1};
    wgpu::RenderPassDepthStencilAttachment d{};
    d.view=depth.CreateView(); d.depthLoadOp=wgpu::LoadOp::Clear; d.depthStoreOp=wgpu::StoreOp::Store; d.depthClearValue=1;
    wgpu::RenderPassDescriptor r{}; r.colorAttachmentCount=1; r.colorAttachments=&c; r.depthStencilAttachment=&d;
    auto pass=encoder.BeginRenderPass(&r);
    pass.SetPipeline(near_pipeline); pass.SetBindGroup(0,near_group); pass.Draw(3);
    // A second blend must fail depth: otherwise red changes from 128 to 192.
    pass.SetPipeline(far_pipeline); pass.SetBindGroup(0,far_group); pass.Draw(3); pass.End();
    wgpu::TexelCopyTextureInfo from{},to{}; from.texture=color; to.texture=copy;
    const wgpu::Extent3D size{32,32,1}; encoder.CopyTextureToTexture(&from,&to,&size);
    wgpu::BufferDescriptor bd{}; bd.usage=wgpu::BufferUsage::CopyDst|wgpu::BufferUsage::MapRead; bd.size=256*32;
    auto readback=device.CreateBuffer(&bd);
    wgpu::TexelCopyBufferInfo out{}; out.buffer=readback; out.layout.bytesPerRow=256; out.layout.rowsPerImage=32;
    encoder.CopyTextureToBuffer(&to,&out,&size);
    auto command=encoder.Finish(); aurora::webgpu::g_queue.Submit(1,&command);
    auto done=std::make_shared<std::atomic<int>>(0);
    readback.MapAsync(wgpu::MapMode::Read,0,256*32,wgpu::CallbackMode::AllowSpontaneous,
      [done](wgpu::MapAsyncStatus status,wgpu::StringView) { done->store(status==wgpu::MapAsyncStatus::Success ? 1 : -1); });
    const auto until=std::chrono::steady_clock::now()+std::chrono::seconds(5);
    while (*done==0 && std::chrono::steady_clock::now()<until) {
      aurora::webgpu::g_instance.ProcessEvents(); std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    if (*done!=1) { readback.Destroy(); return verdict(false,"async-readback-completion"); }
    const auto* data=static_cast<const uint8_t*>(readback.GetConstMappedRange());
    bool valid=data!=nullptr;
    if (data) {
      for (unsigned y=0;y<32;++y) for (unsigned x=0;x<32;++x) {
        const auto* p=data+y*256+x*4;
        valid &= std::abs(int(p[0])-128)<=1 && p[1]==0 && std::abs(int(p[2])-127)<=1 && p[3]==255;
      }
      note("READBACK rgba=%u,%u,%u,%u expected=128,0,127,255 tolerance=1",data[0],data[1],data[2],data[3]);
    }
    readback.Unmap();
    return verdict(valid,"texture-depth-blend-offscreen-copy-readback");
  }
};
bool white_snapshot(const wgpu::Texture& texture,const char* name) {
  if (!texture) return verdict(false,name);
  checkpoint(name);
  auto device=aurora::webgpu::g_device;
  auto encoder=device.CreateCommandEncoder();
  wgpu::BufferDescriptor descriptor{};
  descriptor.usage=wgpu::BufferUsage::CopyDst|wgpu::BufferUsage::MapRead; descriptor.size=256*32;
  auto buffer=device.CreateBuffer(&descriptor);
  wgpu::TexelCopyTextureInfo source{}; source.texture=texture;
  wgpu::TexelCopyBufferInfo target{}; target.buffer=buffer; target.layout.bytesPerRow=256; target.layout.rowsPerImage=32;
  const wgpu::Extent3D size{32,32,1}; encoder.CopyTextureToBuffer(&source,&target,&size);
  auto commands=encoder.Finish(); aurora::webgpu::g_queue.Submit(1,&commands);
  auto done=std::make_shared<std::atomic<int>>(0);
  buffer.MapAsync(wgpu::MapMode::Read,0,256*32,wgpu::CallbackMode::AllowSpontaneous,
    [done](wgpu::MapAsyncStatus status,wgpu::StringView) { done->store(status==wgpu::MapAsyncStatus::Success ? 1 : -1); });
  const auto until=std::chrono::steady_clock::now()+std::chrono::seconds(5);
  while (*done==0 && std::chrono::steady_clock::now()<until) {
    aurora::webgpu::g_instance.ProcessEvents(); std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }
  if (*done!=1) { buffer.Destroy(); return verdict(false,name); }
  const auto* pixels=static_cast<const uint8_t*>(buffer.GetConstMappedRange());
  bool pass=pixels!=nullptr;
  if (pixels) for (unsigned y=0;y<32;++y) for (unsigned x=0;x<32*4;++x) pass &= pixels[y*256+x]==255;
  buffer.Unmap(); return verdict(pass,name);
}
void triangle(bool white=false,unsigned width=1280,unsigned height=720) {
  GXSetCopyClear(GXColor{8,12,28,255},GX_MAX_Z24); GXClearVtxDesc();
  GXSetVtxDesc(GX_VA_POS,GX_DIRECT); GXSetVtxDesc(GX_VA_CLR0,GX_DIRECT);
  GXSetVtxAttrFmt(GX_VTXFMT0,GX_VA_POS,GX_POS_XYZ,GX_F32,0);
  GXSetVtxAttrFmt(GX_VTXFMT0,GX_VA_CLR0,GX_CLR_RGBA,GX_RGBA8,0);
  GXSetNumChans(1); GXSetNumTexGens(white ? 1 : 0); GXSetNumTevStages(1);
  GXSetChanCtrl(GX_COLOR0A0,GX_DISABLE,GX_SRC_REG,GX_SRC_VTX,GX_LIGHT_NULL,GX_DF_NONE,GX_AF_NONE);
  if (white) {
    alignas(32) static const auto pixels=[] { std::array<u8,64> value{}; value.fill(255); return value; }();
    static GXTexObj texture{};
    static bool initialized=false;
    if (!initialized) {
      GXInitTexObj(&texture,pixels.data(),4,4,GX_TF_RGBA8,GX_CLAMP,GX_CLAMP,GX_FALSE);
      GXInitTexObjLOD(&texture,GX_NEAR,GX_NEAR,0,0,0,GX_FALSE,GX_FALSE,GX_ANISO_1);
      initialized=true;
    }
    GXSetVtxDesc(GX_VA_TEX0,GX_DIRECT);
    GXSetVtxAttrFmt(GX_VTXFMT0,GX_VA_TEX0,GX_TEX_ST,GX_F32,0);
    GXSetTexCoordGen(GX_TEXCOORD0,GX_TG_MTX2x4,GX_TG_TEX0,GX_IDENTITY);
    GXLoadTexObj(&texture,GX_TEXMAP0);
    GXSetTevOrder(GX_TEVSTAGE0,GX_TEXCOORD0,GX_TEXMAP0,GX_COLOR0A0);
    GXSetTevOp(GX_TEVSTAGE0,GX_MODULATE);
  } else {
    GXSetTevOrder(GX_TEVSTAGE0,GX_TEXCOORD_NULL,GX_TEXMAP_NULL,GX_COLOR0A0);
    GXSetTevOp(GX_TEVSTAGE0,GX_PASSCLR);
  }
  GXSetCullMode(GX_CULL_NONE); GXSetZMode(GX_DISABLE,GX_ALWAYS,GX_DISABLE);
  GXSetBlendMode(GX_BM_NONE,GX_BL_ONE,GX_BL_ZERO,GX_LO_CLEAR);
  GXSetColorUpdate(GX_TRUE); GXSetAlphaUpdate(GX_TRUE);
  GXSetAlphaCompare(GX_ALWAYS,0,GX_AOP_AND,GX_ALWAYS,0);
  Mtx model{{1,0,0,0},{0,1,0,0},{0,0,1,0}};
  // C_MTXOrtho's near=0, far=1 contract maps view z=-0.5 to GX clip z=-0.5.
  Mtx44 projection{{1,0,0,0},{0,1,0,0},{0,0,-1,-1},{0,0,0,1}};
  GXLoadPosMtxImm(model,GX_PNMTX0); GXSetCurrentMtx(GX_PNMTX0); GXSetProjection(projection,GX_ORTHOGRAPHIC);
  GXSetViewport(0,0,width,height,0,1); GXSetScissor(0,0,width,height);
  GXBegin(GX_TRIANGLES,GX_VTXFMT0,3);
  GXPosition3f32(white ? -1.f : -.8f,white ? -1.f : -.7f,-.5f); GXColor4u8(255,white ? 255 : 0,white ? 255 : 0,255);
  if (white) GXTexCoord2f32(0,0);
  GXPosition3f32(white ? 3.f : .8f,white ? -1.f : -.7f,-.5f); GXColor4u8(white ? 255 : 0,255,white ? 255 : 0,255);
  if (white) GXTexCoord2f32(2,0);
  GXPosition3f32(white ? -1.f : 0,white ? 3.f : .8f,-.5f); GXColor4u8(white ? 255 : 0,white ? 255 : 0,255,255);
  if (white) GXTexCoord2f32(0,2);
  GXEnd();
}
}
int main(int argc,char** argv) {
  platform_init("PSWaker disc-free diagnostic prototype");
  mkdir("/data/pswaker-diagnostic-prototype/cache",0777);
  evidence=std::fopen("/data/pswaker-diagnostic-prototype/diagnostic.log","a");
  if (!evidence) catchReturnFromMain(1);
  note("BEGIN build=%s; console/homebrew baseline is owner-reported and must be confirmed per run",PSWAKER_BUILD_ID);
  if (FILE* manifest=std::fopen("/app0/build-info.json","r")) {
    char line[1024]; while (std::fgets(line,sizeof line,manifest)) note("MANIFEST %s",line);
    verdict(std::fclose(manifest)==0,"manifest-close");
  } else verdict(false,"build-manifest-open");
  checkpoint("runtime-preflight"); verdict(runtime_preflight_entry()==0,"runtime-preflight");
  int launch=0;
  if (FILE* state=std::fopen("/data/pswaker-diagnostic-prototype/preflight-state.txt","r")) {
    verdict(std::fscanf(state,"%d",&launch)==1,"launch-identity-read");
    verdict(std::fclose(state)==0,"launch-identity-close");
  } else verdict(false,"launch-identity-open");
  unsigned cache_entries=0;
  if (DIR* cache=opendir("/data/pswaker-diagnostic-prototype/cache")) {
    while (const auto* entry=readdir(cache)) if (entry->d_name[0]!='.') ++cache_entries;
    verdict(closedir(cache)==0,"cache-inspection-close");
  } else verdict(false,"cache-inspection-open");
  note("RUN launch=%d cache-entries-before-Aurora=%u; owner must label cold/warm and confirm baseline",launch,cache_entries);
  AuroraConfig c{};
  c.appName="PSWaker platform diagnostic prototype";
  c.userPath="/data/pswaker-diagnostic-prototype"; c.cachePath="/data/pswaker-diagnostic-prototype/cache";
  c.resourcesPath="/app0"; c.desiredBackend=BACKEND_VULKAN; c.windowWidth=1920; c.windowHeight=1080;
  c.vsync=true; c.msaa=1; c.maxTextureAnisotropy=1; c.logCallback=logger; c.logLevel=LOG_INFO;
  checkpoint("aurora-initialize"); const auto info=aurora_initialize(argc,argv,&c);
  verdict(info.backend==BACKEND_VULKAN,"selected-Vulkan-backend");
  const auto& adapter=aurora::webgpu::g_adapterInfo;
  note("ADAPTER vendor=%u device=%u description=%.*s",adapter.vendorID,adapter.deviceID,
    int(std::min(adapter.description.length,size_t(512))),adapter.description.data ? adapter.description.data : "");
  AuroraSetViewportPolicy(AURORA_VIEWPORT_NATIVE);
  aurora::window::set_frame_buffer_scale(2.f/3.f);
  // Process Aurora's deferred sizing events so GX coordinates are native target pixels.
  aurora_update();
  u32 internal_width=0,internal_height=0;
  AuroraGetRenderSize(&internal_width,&internal_height);
  verdict(internal_width==1280 && internal_height==720,"internal-render-size");
  note("RESOLUTION internal=%ux%u surface=%ux%u; inspect platform log for actual display mode",internal_width,internal_height,
    aurora::webgpu::g_graphicsConfig.surfaceConfiguration.width,aurora::webgpu::g_graphicsConfig.surfaceConfiguration.height);
  checkpoint("synthetic-audio"); verdict(SDL_InitSubSystem(SDL_INIT_AUDIO),"SDL-audio-init");
  SDL_AudioSpec spec{}; spec.freq=48000; spec.channels=2; spec.format=SDL_AUDIO_S16;
  auto* audio=SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,&spec,audio_callback,nullptr);
  verdict(audio!=nullptr,"SDL-audio-stream"); if (audio) verdict(SDL_ResumeAudioStreamDevice(audio),"SDL-audio-resume");
  Targets targets; targets.recreate();
  unsigned checks=0,frames=0,disconnects=0,reconnects=0;
  bool previous=false,seen_pad=false,awaiting_resume=false,resume_ready=false,exiting=false;
  int32_t user=-1; verdict(sceUserServiceGetInitialUser(&user)==0,"initial-user");
  const auto start=std::chrono::steady_clock::now(); auto next_check=start,next_resource=start;
  checkpoint("ten-minute-loop");
  while (!exiting) {
    for (const auto* event=aurora_update();event && event->type!=AURORA_NONE;++event) if (event->type==AURORA_EXIT) exiting=true;
    const auto now=std::chrono::steady_clock::now(); const double elapsed=std::chrono::duration<double>(now-start).count();
    OrbisPadData raw{}; const int handle=scePadGetHandle(user,0,0);
    const int read_result=handle>=0 ? scePadReadState(handle,&raw) : handle;
    const bool connected=read_result==0 && raw.connected;
    if (connected!=previous) {
      note("PAD connected=%d read-result=%d",connected,read_result);
      if (!connected && seen_pad) { ++disconnects; awaiting_resume=true; resume_ready=false; }
      if (connected) { if (seen_pad) ++reconnects; seen_pad=true; } previous=connected;
    }
    if (!connected) raw={};
    if (!connected && seen_pad) {
      pad neutral{}; pad_player(0,&neutral);
      if (neutral.held || neutral.left_x || neutral.left_y || neutral.right_x || neutral.right_y || neutral.l2 || neutral.r2)
        verdict(false,"inherited-input-neutral-on-disconnect");
    }
    if (awaiting_resume && connected && !(raw.buttons&ORBIS_PAD_BUTTON_CROSS)) resume_ready=true;
    if (awaiting_resume && connected && resume_ready && (raw.buttons&ORBIS_PAD_BUTTON_CROSS)) awaiting_resume=false;
    if (connected && (raw.buttons&ORBIS_PAD_BUTTON_OPTIONS)) exiting=true;
    const bool capture=now>=next_check && elapsed<=600;
    if (capture) {
      // ImGui stores the preview's raw view handle in queued frame packets.
      // Finish encoding earlier packets before replacing that view.
      aurora::gfx::synchronize();
      if (checks && checks%12==0) targets.recreate();
      targets.verify(); ++checks; next_check=now+std::chrono::seconds(5);
    }
    if (now>=next_resource) {
      uint64_t garlic=0,onion=0,buffers=0; ac_ps4_get_memory(&garlic,&onion,&buffers);
      size_t flexible_available=0;
      const int memory_result=sceKernelAvailableFlexibleMemorySize(&flexible_available);
      verdict(memory_result==0,"flexible-memory-query");
      note("RESOURCE seconds=%.1f garlic=%llu onion=%llu buffers=%llu heap-capacity=%zu main-mspace-allocated=%zu flexible-available=%zu audio-frames=%llu audio-errors=%d",
        elapsed,(unsigned long long)garlic,(unsigned long long)onion,(unsigned long long)buffers,ps4rt_heap_size(),pswaker_heap_used(),flexible_available,
        (unsigned long long)audio_frames.load(),audio_errors.load()); next_resource=now+std::chrono::seconds(30);
    }
    if (!aurora_begin_frame()) { std::this_thread::sleep_for(std::chrono::milliseconds(1)); continue; }
    triangle(true);
    aurora::gfx::ResolvedTargets efb_snapshot{},offscreen_snapshot{};
    if (capture) {
      checkpoint("Aurora-EFB-and-offscreen-resolve");
      verdict(aurora::gfx::resolve_pass({},efb_snapshot),"Aurora-EFB-copy");
      if (verdict(aurora::gfx::create_pass(32,32),"Aurora-offscreen-create")) {
        triangle(true,32,32);
        verdict(aurora::gfx::resolve_pass({},offscreen_snapshot),"Aurora-offscreen-resolve");
      }
    }
    triangle();
    ImGui::SetNextWindowPos(ImVec2(25,25),ImGuiCond_Always); ImGui::SetNextWindowSize(ImVec2(780,390),ImGuiCond_Always);
    ImGui::Begin("Disc-free diagnostic",nullptr,ImGuiWindowFlags_NoResize|ImGuiWindowFlags_NoCollapse);
    ImGui::Text("Build %s",PSWAKER_BUILD_ID);
    ImGui::Text("Prototype | %.1f / 600 seconds | frames %u",elapsed,frames++);
    ImGui::Text("Checks %u | failures %d | audio errors %d",checks,errors.load(),audio_errors.load());
    AuroraGetRenderSize(&internal_width,&internal_height);
    ImGui::Text("Internal %ux%u | surface %ux%u",internal_width,internal_height,
      aurora::webgpu::g_graphicsConfig.surfaceConfiguration.width,aurora::webgpu::g_graphicsConfig.surfaceConfiguration.height);
    ImGui::Text("Pad %d | disconnects %u | reconnects %u",connected,disconnects,reconnects);
    ImGui::Text("Buttons %08x | L2 %u | R2 %u",raw.buttons,raw.analogButtons.l2,raw.analogButtons.r2);
    ImGui::Text("Disconnect/reconnect once. Cross resumes; Options closes.");
    if (awaiting_resume) ImGui::Text("Waiting for Cross after reconnect.");
    ImGui::Text("Expected: RGB triangle, purple swatch, quiet continuous tone.");
    if (elapsed>=600) ImGui::Text("Loop complete. Retrieve logs; owner observation still required.");
    ImGui::Text("/data/pswaker-diagnostic-prototype/");
    ImGui::Image((ImTextureID)(uintptr_t)targets.preview.Get(),ImVec2(150,90)); ImGui::End();
    aurora_end_frame();
    if (capture) {
      aurora::gfx::synchronize();
      white_snapshot(efb_snapshot.colorTexture,"Aurora-EFB-known-white-readback");
      white_snapshot(offscreen_snapshot.colorTexture,"Aurora-offscreen-known-white-readback");
    }
  }
  checkpoint("shutdown"); if (audio) SDL_DestroyAudioStream(audio);
  verdict(audio_errors==0,"synthetic-audio-API-errors");
  verdict(disconnects>0 && reconnects>0 && !awaiting_resume,"controller-disconnect-reconnect-resume");
  verdict(std::chrono::steady_clock::now()-start>=std::chrono::seconds(600),"ten-minute-loop");
  note("END frames=%u checks=%u failures=%d; owner observations/resource review required",frames,checks,errors.load());
  aurora_shutdown(); targets={};
  std::fflush(evidence); fsync(fileno(evidence)); std::fclose(evidence);
  catchReturnFromMain(errors ? 1 : 0);
}
