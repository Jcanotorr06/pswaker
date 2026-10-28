// Disc-free checks through GX commands and actual asynchronous texture readbacks.
bool renderer_case(RendererScene scene,const char* name) {
  if (!aurora_begin_frame()) return verdict(false,"renderer-case-begin-frame");
  const bool created=aurora::gfx::create_pass(32,32);
  aurora::gfx::ResolvedTargets snapshot{};
  if (created) triangle(true,32,32,scene);
  const bool resolved=created && aurora::gfx::resolve_pass({},snapshot);
  aurora_end_frame();
  aurora::gfx::synchronize();
  if (!verdict(resolved,name)) return false;
  const bool alpha=scene>=RendererScene::AlphaR8GT && scene<=RendererScene::AlphaBGR24EQFalse;
  const uint8_t opacity=scene>=RendererScene::AlphaR8GTFalse && scene<=RendererScene::AlphaBGR24EQFalse ? 0 : 255;
  return rgba_snapshot(snapshot.colorTexture,name,alpha ? std::array<uint8_t,4>{0,0,0,opacity}
                                                       : std::array<uint8_t,4>{255,255,255,255});
}
bool renderer_checks() {
  checkpoint("Wind-Waker-renderer-known-results");
  bool pass=true;
  constexpr std::pair<RendererScene,const char*> cases[]={
    {RendererScene::AlphaR8GT,"GX-alpha-R8-GT"},{RendererScene::AlphaR8EQ,"GX-alpha-R8-EQ"},
    {RendererScene::AlphaGR16GT,"GX-alpha-GR16-GT"},{RendererScene::AlphaGR16EQ,"GX-alpha-GR16-EQ"},
    {RendererScene::AlphaBGR24GT,"GX-alpha-BGR24-GT"},{RendererScene::AlphaBGR24EQ,"GX-alpha-BGR24-EQ"},
    {RendererScene::AlphaR8GTFalse,"GX-alpha-R8-GT-false"},{RendererScene::AlphaR8EQFalse,"GX-alpha-R8-EQ-false"},
    {RendererScene::AlphaGR16GTFalse,"GX-alpha-GR16-GT-false"},{RendererScene::AlphaGR16EQFalse,"GX-alpha-GR16-EQ-false"},
    {RendererScene::AlphaBGR24GTFalse,"GX-alpha-BGR24-GT-false"},{RendererScene::AlphaBGR24EQFalse,"GX-alpha-BGR24-EQ-false"},
    {RendererScene::LitSrtg,"GX-lit-SRTG"},{RendererScene::QuadTriangle,"GX-three-vertex-quad"},
    {RendererScene::ZeroBrightnessLight,"GX-zero-brightness-attenuation"}};
  for (const auto& [scene,name]:cases) pass=renderer_case(scene,name) && pass;

  if (!aurora_begin_frame()) return verdict(false,"GX-copy-begin-frame");
  triangle(true);
  alignas(32) static std::array<u8,32*32*4> copy_pixels{};
  GXSetTexCopySrc(0,0,1280,720); GXSetTexCopyDst(32,32,GX_TF_RGBA8,GX_FALSE);
  GXCopyTex(copy_pixels.data(),GX_FALSE);
  GXTexObj copy_texture{};
  GXInitTexObj(&copy_texture,copy_pixels.data(),32,32,GX_TF_RGBA8,GX_CLAMP,GX_CLAMP,GX_FALSE);
  GXInitTexObjLOD(&copy_texture,GX_NEAR,GX_NEAR,0,0,0,GX_FALSE,GX_FALSE,GX_ANISO_1);
  aurora::gfx::ResolvedTargets copy_snapshot{};
  const bool created=aurora::gfx::create_pass(32,32);
  if (created) triangle(true,32,32,RendererScene::Standard,&copy_texture);
  const bool copied=created && aurora::gfx::resolve_pass({},copy_snapshot);
  aurora_end_frame(); aurora::gfx::synchronize();
  pass=verdict(copied,"GX-EFB-copy-to-texture-resolve") && pass;
  if (copied) pass=white_snapshot(copy_snapshot.colorTexture,"GX-EFB-copy-to-texture-known-white") && pass;

  // Allocation is unchanged while the second draw maps into just the upper-left quarter.
  AuroraSetViewportPolicy(AURORA_VIEWPORT_STRETCH); aurora_update();
  if (!aurora_begin_frame()) return verdict(false,"content-scale-begin-frame");
  triangle(true,640,480);
  AuroraSetContentScale(.5f);
  triangle(true,640,480,RendererScene::Black);
  AuroraSetContentScale(1.f);
  aurora::gfx::ResolvedTargets snapshot{};
  const bool resolved=aurora::gfx::resolve_pass({},snapshot);
  aurora_end_frame(); aurora::gfx::synchronize();
  pass=verdict(resolved && snapshot.width==1280 && snapshot.height==720,"GX-content-scale-allocation") && pass;
  if (resolved && snapshot.width>=64 && snapshot.height>=64) {
    pass=rgba_snapshot(snapshot.colorTexture,"GX-content-scale-upper-left",{0,0,0,255}) && pass;
    pass=rgba_snapshot(snapshot.colorTexture,"GX-content-scale-lower-right",{255,255,255,255},snapshot.width-32,snapshot.height-32) && pass;
  }
  AuroraSetViewportPolicy(AURORA_VIEWPORT_NATIVE); aurora_update();
  return pass;
}
