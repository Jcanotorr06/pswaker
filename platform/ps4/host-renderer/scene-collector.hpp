// Included only by the maintainer collector. These packets are the game's
// implementations; no player, stage process, weather controller or save runs.
#include "d/actor/d_a_sea.h"
#include "d/d_kankyo.h"
#include "m_Do/m_Do_graphic.h"
#include <aurora/gfx.hpp>
#include "gfx/frame_packet.hpp"

static view_class sceneView{};

static void scene_world(bool night = false, bool dense = false, bool range = false, bool raised = false) {
  sceneView.mNear = raised ? 10.0f : 1.0f;
  sceneView.mFar = raised ? 80000.0f : 160000.0f;
  sceneView.mFovy = raised ? 60.0f : 45.0f;
  sceneView.mAspect = 4.0f / 3.0f;
  Mtx44 projection;
  MTXPerspective(projection, sceneView.mFovy, sceneView.mAspect, sceneView.mNear, sceneView.mFar);
  GXSetProjection(projection, GX_PERSPECTIVE);
  Mtx view;
  cXyz eye(0, raised ? 3000.0f : 1000.0f, 2000), target(0, 0, -2000), up(0, 1, 0);
  MTXLookAt(view, &eye, &up, &target);
  j3dSys.setViewMtx(view);
  dComIfGd_setView(&sceneView);
  g_env_light.mBG1_C0 = night ? GXColorS10{10, 20, 40, 255} : GXColorS10{80, 160, 200, 255};
  g_env_light.mBG1_K0 = night ? GXColorS10{5, 10, 20, 255} : GXColorS10{20, 80, 120, 255};
  g_env_light.mFogColor = g_env_light.mBG1_C0;
  g_env_light.mVrUsoUmiColor = g_env_light.mBG1_C0;
  g_env_light.mFogStartZ__setLight = dense ? 100.0f : 1000.0f;
  g_env_light.mFogEndZ__setLight = dense ? 5000.0f : 50000.0f;
  g_env_light.mFogAdjEnable = range;
  g_env_light.mFogAdjCenter = 320;
  g_env_light.mFogAdjTableType = 0;
}

static daSea_packet_c* scene_sea() {
  auto* sea = new daSea_packet_c();
  cXyz origin(0, 0, 0);
  check(sea->create(origin), "create real ocean packet");
  // create() initializes the real flat height table. execute() needs the stage,
  // camera and player controllers; this recipe fixes its grid bounds instead.
  sea->mDrawMinX = sea->mDrawMinZ = -25600;
  sea->mDrawMaxX = sea->mDrawMaxZ = 25600;
  sea->mCullStopFlag = 0;
  return sea;
}

static void scene_shadow(bool textured, bool sloped = false) {
  cXyz position(0, sloped ? 200.0f : 50.0f, 0);
  cXyz normal(sloped ? 0.6f : 0.0f, sloped ? 0.8f : 1.0f, 0);
  check(dComIfGd_setSimpleShadow(&position, 0, 100, &normal, sloped ? 4096 : 0,
        sloped ? 2.0f : 1.0f, textured ? dDlst_shadowControl_c::getSimpleTex() : nullptr), "set real simple shadow");
  dComIfGd_drawShadow(j3dSys.getViewMtx());
}

static void scene_alpha(u8 type, u8 alpha) {
  Mtx transform;
  MTXScale(transform, 100, 100, 100);
  dDlst_alphaModelPacket packet;
  packet.mType = type;
  packet.mColor = GXColor{255, 200, 100, alpha};
  packet.mMtxP = &transform;
  packet.draw();
}

static std::vector<ActorState> scene_states(const char* scenario) {
  dDlst_shadowControl_c::setSimpleTex(dComIfG_getObjectRes("Always", dRes_INDEX_ALWAYS_I4_BALL128B_e));
  if (!strcmp(scenario, "scene-simple-shadows-v1"))
    return {{"untextured", [] { scene_world(); scene_shadow(false); }},
            {"textured", [] { scene_world(); scene_shadow(true); }},
            {"sloped-raised", [] { scene_world(false, false, false, true); scene_shadow(true, true); }},
            {"textured-repeated", [] { scene_world(); scene_shadow(true); }}};
  auto* sea = scene_sea();
  if (!strcmp(scenario, "scene-ocean-world-v1"))
    return {{"day", [=] { scene_world(); sea->draw(); }},
            {"night", [=] { scene_world(true); sea->draw(); }},
            {"dense-fog", [=] { scene_world(false, true); sea->draw(); }},
            {"range-adjusted", [=] { scene_world(false, false, true); sea->draw(); }},
            {"camera-raised", [=] { scene_world(false, false, false, true); sea->draw(); }},
            {"day-repeated", [=] { scene_world(); sea->draw(); }}};
  return {{"sphere", [] { scene_world(); scene_alpha(0, 255); }},
          {"cube", [] { scene_world(); scene_alpha(3, 255); }},
          {"sphere-faded", [] { scene_world(); scene_alpha(0, 128); }},
          {"sea-shadow-sphere", [=] { scene_world(); sea->draw(); scene_shadow(true); scene_alpha(0, 128); }},
          {"sphere-repeated", [] { scene_world(); scene_alpha(0, 255); }}};
}

static unsigned draw_scene_states(const std::vector<ActorState>& states) {
  unsigned draws = 0;
  for (unsigned index = 0; index < states.size(); ++index) {
    effectSteps.push_back({index, index + 1, 0, 0});
    activeStep = &effectSteps.back();
    begin_draw();
    dComIfGd_reset();
    mDoGph_gInf_c::free();
    states[index].entry();
    activeStep->draws = end_draw();
    fprintf(stderr, "scene state %s: draws=%u lookups=%u\n", states[index].name, activeStep->draws, activeStep->lookups);
    check(activeStep->draws && activeStep->lookups, "each scene state must actually draw");
    draws += activeStep->draws;
    activeStep = nullptr;
  }
  return draws;
}

static void write_scene_layout(FILE* report, const RenderTargetLayout& layout, const char* role) {
  fprintf(report, "{\"role\":\"%s\",\"key\":%llu,\"attachments\":%u,\"color_format\":%u,\"depth_format\":%u,"
          "\"samples\":%u,\"width\":%u,\"height\":%u}",
          role, static_cast<unsigned long long>(layout.key), layout.colorAttachmentCount,
          static_cast<uint32_t>(layout.colorAttachments[0].format), static_cast<uint32_t>(layout.depthStencilFormat),
          layout.sampleCount, layout.colorAttachments[0].width, layout.colorAttachments[0].height);
}

static void write_scene_report(FILE* report, const char* scenario, const std::vector<ActorState>& states,
                               unsigned draws, unsigned runtimeRows, const RenderTargetLayout& scene,
                               const RenderTargetLayout& offscreen, bool presentation = false) {
  fprintf(report, "{\"schema\":1,\"scenario\":\"%s\",\"method\":\"%s\","
          "\"resource\":\"/res/Object/Always.arc\",\"draw_calls\":%u,\"pipeline_lookups\":%u,"
          "\"runtime_identity_verified_rows\":%u,\"frames\":%zu,\"script\":{\"states\":[",
          scenario, presentation ? "scripted-presentation-draw" : "scripted-scene-draw",
          draws, drawCalls, runtimeRows, states.size());
  for (size_t i = 0; i < states.size(); ++i) fprintf(report, "%s\"%s\"", i ? "," : "", states[i].name);
  fprintf(report, "],\"frames_per_state\":1,\"setup\":\"%s\"},\"unhandled_states\":%s,\"preparation_layouts\":[",
          presentation ? "fixed-presentation-v1" : "fixed-scene-world-camera-v1",
          presentation ? "[\"menu-controllers-and-layouts\",\"story-and-camera-controllers\",\"framebuffer-effects\","
                         "\"player-animation-and-attachments\",\"unreachable-one-time-states\"]"
                       : "[\"stage-and-weather-controllers\",\"wave-simulation\",\"real-shadow-receivers\","
                         "\"mirrors-and-reflections\",\"other-camera-and-effect-combinations\"]");
  write_scene_layout(report, scene, "scene");
  fprintf(report, ",");
  write_scene_layout(report, offscreen, "offscreen");
  fprintf(report, "],\"states\":[");
  for (size_t i = 0; i < effectSteps.size(); ++i) {
    const auto& step = effectSteps[i];
    fprintf(report, "%s{\"tick\":%u,\"state\":\"%s\",\"draw_calls\":%u,\"pipeline_lookups\":%u,"
            "\"layout_keys\":[%llu],\"configurations\":[", i ? "," : "", step.tick, states[i].name,
            step.draws, step.lookups, static_cast<unsigned long long>(observedLayout.key));
    for (size_t k = 0; k < step.configurations.size(); ++k)
      fprintf(report, "%s{\"type\":1,\"hash\":%lld}", k ? "," : "", static_cast<long long>(step.configurations[k]));
    fprintf(report, "]}");
  }
  fprintf(report, "]");
}
