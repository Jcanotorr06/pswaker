// Maintainer-only model/effect draws. Linked to the same prepared game and GX renderer
// as the PS4 program; never entered from the player executable.
#include <aurora/aurora.h>
#include <aurora/dvd.h>
#include <aurora/gfx.h>
#include <dolphin/dvd.h>
#include <dolphin/os.h>
#include <dolphin/vi.h>
#include <dolphin/gx/GXAurora.h>
#include "JSystem/JKernel/JKRExpHeap.h"
#include "JSystem/JKernel/JKRArchive.h"
#include "JSystem/JKernel/JKRDvdRipper.h"
#include "JSystem/JMath/JMath.h"
#include "JSystem/J3DGraphLoader/J3DModelLoader.h"
#include "JSystem/J3DGraphAnimator/J3DModel.h"
#include "JSystem/J3DGraphAnimator/J3DModelData.h"
#include "JSystem/J3DGraphBase/J3DDrawBuffer.h"
#include "JSystem/J3DGraphBase/J3DMaterial.h"
#include "JSystem/J3DGraphAnimator/J3DJoint.h"
#include "res/Object/Always.h"
#include "res/Object/Bgn.h"
#include "res/Object/Bk.h"
#include "res/Object/Bpw.h"
#include "res/Object/Btd.h"
#include "res/Object/Cc.h"
#include "res/Object/Link.h"
#include "res/Object/Ph.h"
#include "res/Object/System.h"
#include "m_Do/m_Do_dvd_thread.h"
#include "m_Do/m_Do_ext.h"
#include "JSystem/JParticle/JPAEmitterManager.h"
#include "JSystem/JParticle/JPAResourceManager.h"
#include "d/d_com_inf_game.h"
#include "d/d_material.h"
#include "d/d_particle.h"
#include "d/d_particle_name.h"
#include "gx/pipeline.hpp"
#include "gfx/resources.hpp"
#include "frame-pacing.hpp"
#include <sqlite3.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <functional>
#include <mutex>
#include <algorithm>
#include <cctype>
#include <string>
#include <vector>
#include <memory>

static sqlite3* observed;
static std::mutex observationMutex;
static unsigned drawCalls;
static aurora::gfx::RenderTargetLayout observedLayout;
struct EffectStep {
  unsigned variant, tick, particles, emitters, draws = 0, lookups = 0;
  std::vector<sqlite3_int64> configurations;
};
static std::vector<EffectStep> effectSteps;
static EffectStep* activeStep;
static bool recording;
static void check(bool ok, const char* message) {
  if (!ok) { fprintf(stderr, "collector: %s\n", message); fflush(stderr); std::_Exit(1); }
}

static unsigned verify_runtime_identities(const char* assets) {
  sqlite3* baseline = nullptr;
  const auto path = (std::filesystem::path(assets) / "initial_pipeline_cache.db").string();
  check(sqlite3_open_v2(path.c_str(), &baseline, SQLITE_OPEN_READONLY, nullptr) == SQLITE_OK, "open baseline read-only");
  sqlite3_stmt* row = nullptr;
  check(sqlite3_prepare_v2(baseline, "SELECT type,hash,config FROM pipeline_cache", -1, &row, nullptr) == SQLITE_OK,
        "read known runtime descriptions");
  unsigned count = 0;
  int status;
  while ((status = sqlite3_step(row)) == SQLITE_ROW) {
    const auto type = sqlite3_column_int(row, 0);
    const auto bytes = sqlite3_column_bytes(row, 2);
    check((type == 0 && bytes == 8) || (type == 1 && bytes == 2772), "known runtime representation");
    const auto hash = aurora::xxh3_hash_s(sqlite3_column_blob(row, 2), bytes, type);
    check(static_cast<sqlite3_int64>(hash) == sqlite3_column_int64(row, 1), "known runtime identity/hash mismatch");
    ++count;
  }
  check(status == SQLITE_DONE && count > 0, "finish runtime identity comparison");
  sqlite3_finalize(row);
  check(sqlite3_close(baseline) == SQLITE_OK, "close runtime reference");
  return count;
}

using aurora::gfx::PipelineRef;
using aurora::gfx::RenderTargetLayout;
using aurora::gx::PipelineConfig;
extern PipelineRef original_find(const PipelineConfig&, const RenderTargetLayout&)
  asm("__real__ZN6aurora3gfx13find_pipelineERKNS_2gx14PipelineConfigERKNS0_18RenderTargetLayoutE");
PipelineRef observe_find(const PipelineConfig&, const RenderTargetLayout&)
  asm("__wrap__ZN6aurora3gfx13find_pipelineERKNS_2gx14PipelineConfigERKNS0_18RenderTargetLayoutE");
PipelineRef observe_find(const PipelineConfig& config, const RenderTargetLayout& layout) {
  const auto ref = original_find(config, layout);
  if (!recording) return ref;
  const auto key = aurora::xxh3_hash(config, static_cast<aurora::HashType>(aurora::gfx::ShaderType::GX));
  std::lock_guard lock(observationMutex);
  sqlite3_stmt* row = nullptr;
  check(sqlite3_prepare_v2(observed, "INSERT INTO pipeline_cache VALUES(1,?,13,2772,?,0) "
    "ON CONFLICT(type,hash) DO UPDATE SET config=excluded.config "
    "WHERE pipeline_cache.config=excluded.config RETURNING hash",
                          -1, &row, nullptr) == SQLITE_OK, "prepare observation");
  sqlite3_bind_int64(row, 1, static_cast<sqlite3_int64>(key));
  sqlite3_bind_blob(row, 2, &config, sizeof(config), SQLITE_TRANSIENT);
  check(sqlite3_step(row) == SQLITE_ROW, "record observation without identity/description conflict");
  check(sqlite3_step(row) == SQLITE_DONE, "finish observation");
  sqlite3_finalize(row);
  ++drawCalls;
  if (activeStep) {
    ++activeStep->lookups;
    const auto identity = static_cast<sqlite3_int64>(key);
    auto& keys = activeStep->configurations;
    if (std::find(keys.begin(), keys.end(), identity) == keys.end()) keys.push_back(identity);
  }
  check(observedLayout.key == 0 || observedLayout.key == layout.key, "fixed scenario must retain one target layout");
  observedLayout = layout;
  return ref;
}
extern "C" uint64_t pswaker_perf_now() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count();
}
extern "C" void pswaker_perf_shader_wait(uint64_t) {}
extern "C" PswakerFrameTag pswaker_perf_capture() { return {}; }
extern "C" void pswaker_perf_present(PswakerFrameTag) {}
extern "C" void pswaker_perf_present_failed() {}
// These link-only hooks belong to the unused full-game frame loop. Entering
// that loop would violate the bounded collector contract, so fail explicitly.
void pswaker_frame_boundary() { check(false, "game loop is outside this collector"); }
void pswaker_perf_game_frame(uint64_t) { check(false, "game logic is outside this collector"); }
void pswaker_perf_stage(const char*, int) { check(false, "stage loading is outside this collector"); }

static void begin_draw() {
  aurora_update();
  check(aurora_begin_frame(), "begin scenario frame");
  GXSetViewport(0, 0, 640, 480, 0, 1);
  GXSetScissor(0, 0, 640, 480);
  Mtx44 projection;
  MTXPerspective(projection, 45, 4.0f / 3.0f, 1, 10000);
  GXSetProjection(projection, GX_PERSPECTIVE);
  j3dSys.drawInit();
}

static unsigned end_draw() {
  aurora_end_frame();
  aurora::gfx::synchronize();
  return aurora_get_stats()->drawCallCount;
}

static unsigned draw_effect(Mtx view) {
  auto* bytes = JKRDvdToMainRam("/res/Particle/common.jpc", nullptr, EXPAND_SWITCH_UNKNOWN1,
                               0, JKRHeap::getCurrentHeap(), JKRDvdRipper::ALLOC_DIRECTION_FORWARD, 0, nullptr);
  check(bytes, "load common particles through game DVD loader");
  JPAResourceManager resources(bytes, JKRHeap::getCurrentHeap());
  check(resources.getEmitterResource()->getByUserIndex(dPa_name::ID_AK_JN_TUBOKONAGONA),
        "find stock pot debris effect 0x0018");
  // Same common-effect pool sizes as dPa_control_c::createCommon. Scene, actor,
  // model-shard and framebuffer-swap prerequisites are outside this scenario.
  JPAEmitterManager manager(&resources, 3000, 150, 200, JKRHeap::getCurrentHeap());
  JPADrawInfo drawInfo(view, 45, 4.0f / 3.0f);
  unsigned draws = 0;
  for (unsigned texture = 0; texture < 2; ++texture) {
    check(manager.getEmitterNumber() == 0 && manager.getParticleNumber() == 0, "empty initial effect state");
    JPABaseEmitter::emtrInfo.mRandom.setSeed(0);
    dPa_selectTexEcallBack callback(texture);
    JGeometry::TVec3<f32> origin(0, 0, 0), scale(1, 1, 1);
    auto* emitter = manager.createSimpleEmitterID(origin, dPa_name::ID_AK_JN_TUBOKONAGONA, 0, 0, nullptr, nullptr);
    check(emitter, "instantiate stock pot debris");
    // Mirror eff_break_tsubo -> dPa_control_c::set's selected inputs without
    // constructing a stage controller or consulting actor/save/environment state.
    emitter->setGlobalScale(scale);
    emitter->setGlobalAlpha(255);
    emitter->setGlobalPrmColor(255, 255, 255);
    emitter->setGlobalEnvColor(255, 255, 255);
    emitter->setEmitterCallBackPtr(&callback);
    callback.setup(emitter, nullptr, nullptr, -1);
    bool alive = false, complete = false;
    for (unsigned tick = 1; tick <= 180; ++tick) {
      manager.calc(0); // One original particle update per scripted 30 Hz tick.
      effectSteps.push_back({texture, tick, manager.getParticleNumber(), manager.getEmitterNumber()});
      activeStep = &effectSteps.back();
      alive |= activeStep->particles > 0;
      begin_draw();
      j3dSys.reinitGX();
      manager.draw(&drawInfo, 0);
      GXSetAlphaUpdate(GX_DISABLE);
      GXSetNumIndStages(0);
      activeStep->draws = end_draw();
      draws += activeStep->draws;
      activeStep = nullptr;
      if (manager.getEmitterNumber() == 0 && manager.getParticleNumber() == 0) {
        complete = true;
        break;
      }
    }
    check(alive && complete, "effect must emit particles and retire naturally within 180 ticks");
  }
  return draws;
}

static void write_effect_steps(FILE* report) {
  fprintf(report, ",\"variations\":[");
  for (unsigned texture = 0; texture < 2; ++texture) {
    fprintf(report, "%s{\"texture_index\":%u,\"steps\":[", texture ? "," : "", texture);
    bool first = true;
    for (const auto& step : effectSteps) {
      if (step.variant != texture) continue;
      fprintf(report, "%s{\"tick\":%u,\"particles\":%u,\"emitters\":%u,\"draw_calls\":%u,"
              "\"pipeline_lookups\":%u,\"configurations\":[", first ? "" : ",", step.tick,
              step.particles, step.emitters, step.draws, step.lookups);
      first = false;
      for (size_t i = 0; i < step.configurations.size(); ++i)
        fprintf(report, "%s{\"type\":1,\"hash\":%lld}", i ? "," : "",
                static_cast<long long>(step.configurations[i]));
      fprintf(report, "]}");
    }
    fprintf(report, "]}");
  }
  fprintf(report, "]");
}

static std::vector<unsigned> particle_ids(const std::string& resource, bool enemyDeath) {
  const std::string prefix = "/res/Particle/common.jpc:";
  check(resource.starts_with(prefix), "only the fixed common particle bank is supported");
  std::vector<unsigned> ids;
  size_t start = prefix.size();
  while (start < resource.size()) {
    const auto end = resource.find('+', start);
    const auto token = resource.substr(start, end == std::string::npos ? end : end - start);
    check(token.size() == 6 && token.starts_with("0x") &&
          std::all_of(token.begin() + 2, token.end(), [](unsigned char c) { return std::isxdigit(c); }),
          "fixed four-digit effect ID required");
    const unsigned id = std::stoul(token, nullptr, 16);
    check(id == 0x2022 || id == 0x2027 || id == 0x2008 || id == 0x2009 || id == 0x200a ||
          id == 0x000b || id == 0x0013 || id == 0x0018 || id == 0x0019 || id == 0x232a ||
          (enemyDeath && (id == 0x0014 || id == 0x0015 || id == 0x0016 ||
                          id == 0x043c || id == 0x043d || id == 0x043e)),
          "effect requires a separately validated recipe");
    check(ids.size() < 4 && std::find(ids.begin(), ids.end(), id) == ids.end(), "bounded unique effect IDs");
    ids.push_back(id);
    if (end == std::string::npos) break;
    start = end + 1;
  }
  check(!ids.empty() && resource.back() != '+', "particle recipe required");
  return ids;
}

enum class ParticleSetup { Plain, CheapBomb, EnemyDeath };

static unsigned draw_particles(Mtx view, const std::vector<unsigned>& ids, ParticleSetup setup = ParticleSetup::Plain) {
  const bool cheapBomb = setup == ParticleSetup::CheapBomb;
  // daDisappear_c effects use setNormal; the bounded recipes above use the P1 group.
  const auto plainGroup = setup == ParticleSetup::EnemyDeath ? dPa_control_c::dPtclGroup_Normal_e
                                                             : dPa_control_c::dPtclGroup_NormalP1_e;
  auto* bytes = JKRDvdToMainRam("/res/Particle/common.jpc", nullptr, EXPAND_SWITCH_UNKNOWN1,
                               0, JKRHeap::getCurrentHeap(), JKRDvdRipper::ALLOC_DIRECTION_FORWARD, 0, nullptr);
  check(bytes, "load actual common particle bank");
  JPAResourceManager resources(bytes, JKRHeap::getCurrentHeap());
  JPAEmitterManager manager(&resources, 3000, 150, 200, JKRHeap::getCurrentHeap());
  JPADrawInfo drawInfo(view, 45, 4.0f / 3.0f);
  unsigned draws = 0;
  for (unsigned variation = 0; variation < 2; ++variation) {
    check(manager.getEmitterNumber() == 0 && manager.getParticleNumber() == 0, "empty particle manager");
    JPABaseEmitter::emtrInfo.mRandom.setSeed(variation);
    dPa_selectTexEcallBack texture(variation);
    dPa_bombSmokeEcallBack bombSmoke;
    const cXyz smokePosition(0, 0, 0); // Follow callbacks retain this pointer through every tick.
    std::vector<std::unique_ptr<dPa_smokeEcallBack>> smokeCallbacks;
    for (const auto id : ids) {
      JGeometry::TVec3<f32> origin(0, 0, 0), scale(variation ? 2 : 1, variation ? 2 : 1, variation ? 2 : 1);
      const auto group = id & 0x2000 ? dPa_control_c::dPtclGroup_ToonP1_e : plainGroup;
      auto* emitter = manager.createSimpleEmitterID(origin, id, group, 0, nullptr, nullptr);
      check(emitter, "instantiate selected particle effect");
      emitter->setGlobalScale(scale);
      emitter->setGlobalAlpha(variation ? 128 : 255);
      if (setup == ParticleSetup::EnemyDeath && id == 0x0015) {
        // set_disappear -> setNormalStripes(..., 0xFF, 0x96) spirit callback.
        emitter->setEmitterCallBackPtr(&dPa_control_c::mStripes);
        dPa_control_c::mStripes.setup(emitter, nullptr, nullptr, -1);
        emitter->setUserWork(0x96);
      } else if (id == 0x0018) {
        emitter->setEmitterCallBackPtr(&texture);
        texture.setup(emitter, nullptr, nullptr, -1);
      } else if (id == 0x2009 || id == 0x200a || id == 0x232a) {
        emitter->setEmitterCallBackPtr(&bombSmoke);
        emitter->setUserWork(id == 0x2009 ? 0x460501 : 0x280478);
      } else if (id == 0x2022 || id == 0x2027) {
        // Real smoke TEV/vertex callbacks with fixed lighting and no stage wind.
        auto callback = std::make_unique<dPa_smokeEcallBack>(0, 0, 0, 1);
        callback->onWindOff();
        emitter->setEmitterCallBackPtr(callback.get());
        callback->setup(emitter, &smokePosition, nullptr, -1);
        // Selected setSimpleLand inputs, independent of ground collision.
        emitter->setMaxFrame(1);
        emitter->setRate(3.0f);
        emitter->setSpread(0.05f);
        smokeCallbacks.push_back(std::move(callback));
      }
      // Continuous resources get an explicit finite emission window; particles
      // still expire through normal JPA simulation, never forced pool deletion.
      if (emitter->isContinuousParticle()) emitter->setMaxFrame(30);
      // daBomb_c::eff_explode_cheap mutations, applied before the first real tick.
      if (cheapBomb && id == 0x000b) {
        emitter->setLifeTime(12);
        emitter->setGlobalParticleScale(0.5f, 0.67f);
      } else if (cheapBomb && (id == 0x200a || id == 0x2008)) {
        emitter->setLifeTime(70);
        if (id == 0x2008) {
          emitter->setAwayFromAxisSpeed(25.0f);
          emitter->setDirectionalSpeed(35.0f);
        }
      }
    }
    bool alive = false, complete = false;
    for (unsigned tick = 1; tick <= 240; ++tick) {
      manager.calc(plainGroup);
      manager.calc(dPa_control_c::dPtclGroup_ToonP1_e);
      effectSteps.push_back({variation, tick, manager.getParticleNumber(), manager.getEmitterNumber()});
      activeStep = &effectSteps.back();
      alive |= activeStep->particles > 0;
      begin_draw();
      for (const auto group : {plainGroup, dPa_control_c::dPtclGroup_ToonP1_e}) {
        j3dSys.reinitGX();
        manager.draw(&drawInfo, group);
        GXSetAlphaUpdate(GX_DISABLE);
        GXSetNumIndStages(0);
      }
      activeStep->draws = end_draw();
      draws += activeStep->draws;
      activeStep = nullptr;
      if (manager.getEmitterNumber() == 0 && manager.getParticleNumber() == 0) {
        complete = true;
        break;
      }
    }
    check(alive && complete, "particle recipe must draw and retire within 240 ticks");
  }
  return draws;
}

// Actor recipes reuse the game's resource, material and draw-list logic. Actor
// processes, AI, collision, stage lighting and the game loop remain excluded.
struct ActorState {
  const char* name;
  std::function<void()> entry;
};
struct ActorRecipe {
  const char* scenario;
  const char* resource;
  const char* archive;
  std::vector<ActorState> (*states)();
};

static void load_object(const char* name) {
  check(dComIfG_setObjectRes(name, JKRArchive::DEFAULT_MOUNT_DIRECTION, nullptr), "queue object archive");
  // The DVD thread never starts here. Servicing one mDoDvdThd_param_c::mainLoop
  // pass keeps dRes_info_c::loadResource's per-type material and toon-texture setup.
  auto& queue = mDoDvdThd::l_param;
  check(queue.waitForKick(), "receive object archive command");
  auto* command = queue.getFirstCommand();
  check(command, "find object archive command");
  queue.cut(command);
  check(command->execute(), "mount object archive");
  check(dComIfG_syncObjectRes(name) == 0, "prepare object resources");
}

static void create_actor_runtime() {
  auto* root = JKRHeap::getRootHeap();
  check(mDoExt_createCommandHeap(0x100000, root) && mDoExt_createArchiveHeap(0x6000000, root)
        && mDoExt_createGameHeap(0x4000000, root) && mDoExt_createZeldaHeap(0x2000000, root), "create game heaps");
  JKRSetCurrentHeap(mDoExt_getZeldaHeap());
  check(g_dComIfG_gameInfo.drawlist.init(), "create game draw lists");
  load_object("System"); // dScnLogo_c::create toon images, consumed by setToonTex.
  dDlst_list_c::setToonImage((ResTIMG*)dComIfG_getObjectRes("System", dRes_INDEX_SYSTEM_BTI_TOON_e));
  dDlst_list_c::setToonExImage((ResTIMG*)dComIfG_getObjectRes("System", dRes_INDEX_SYSTEM_BTI_TOONEX_e));
  check(dDlst_list_c::getToonImage() && dDlst_list_c::getToonExImage(), "load toon images");
  load_object("Always"); // dScnPly_c::phase_4 shared freeze material.
  dMat_control_c::create((J3DMaterialTable*)dComIfG_getObjectRes("Always", dRes_INDEX_ALWAYS_BMT_ICE_e),
                         (J3DAnmTextureSRTKey*)dComIfG_getObjectRes("Always", dRes_INDEX_ALWAYS_BTK_ICE_e));
}

static mDoExt_McaMorf* actor_morf(const char* archive, int index, u32 modelFlags, u32 listFlags) {
  auto* morf = new mDoExt_McaMorf((J3DModelData*)dComIfG_getObjectRes(archive, index), nullptr, nullptr, nullptr,
                                  J3DFrameCtrl::EMode_NONE, 0.0f, 0, -1, 0, nullptr, modelFlags, listFlags);
  check(morf && morf->getModel(), "create actor model");
  return morf;
}

static mDoExt_brkAnm* actor_brk(J3DModelData* data, const char* archive, int index, int mode = J3DFrameCtrl::EMode_NONE) {
  auto* anm = new mDoExt_brkAnm();
  check(anm && anm->init(data, (J3DAnmTevRegKey*)dComIfG_getObjectRes(archive, index), true, mode),
        "bind actor register animation");
  return anm;
}

static mDoExt_btkAnm* actor_btk(J3DModelData* data, const char* archive, int index, int mode = J3DFrameCtrl::EMode_NONE) {
  auto* anm = new mDoExt_btkAnm();
  check(anm && anm->init(data, (J3DAnmTextureSRTKey*)dComIfG_getObjectRes(archive, index), true, mode),
        "bind actor texture animation");
  return anm;
}

// daBk_Draw material/freeze choices and props, plus br_draw's swing blur with
// useHeapInit's blur tables. Eye masking, BTP blinking and attachment remain gaps.
static std::vector<ActorState> bokoblin_states() {
  auto* morf = actor_morf("Bk", dRes_INDEX_BK_BDL_BK_e, 0x00080000, 0x37221203);
  auto* green = (J3DMaterialTable*)dComIfG_getObjectRes("Bk", dRes_INDEX_BK_BMT_GREEN_e);
  auto* pink = (J3DMaterialTable*)dComIfG_getObjectRes("Bk", dRes_INDEX_BK_BMT_PINK_e);
  auto* club = (J3DMaterialTable*)dComIfG_getObjectRes("Bk", dRes_INDEX_BK_BMT_BK_BOKO_e);
  auto* sword = (J3DMaterialTable*)dComIfG_getObjectRes("Bk", dRes_INDEX_BK_BMT_BK_KEN_e);
  auto* blurData = (J3DModelData*)dComIfG_getObjectRes("Bk", dRes_INDEX_BK_BMD_BK_KB_e);
  blurData->setMaterialTable(club, J3DMatCopyFlag_Material);
  auto* blur = mDoExt_J3DModel__create(blurData, 0, 0x11020203);
  auto* shield = mDoExt_J3DModel__create((J3DModelData*)dComIfG_getObjectRes("Bk", dRes_INDEX_BK_BMD_BK_TATE_e), 0, 0x11020203);
  auto* telescope = mDoExt_J3DModel__create((J3DModelData*)dComIfG_getObjectRes("Bk", dRes_INDEX_BK_BDL_BOUEN_e), 0, 0x11020203);
  check(blur && shield && telescope, "create bokoblin props");
  const auto body = [morf] { morf->calc(); morf->entryDL(); };
  const auto blurDraw = [=](J3DMaterialTable* table, u16 shown) {
    blurData->setMaterialTable(table, J3DMatCopyFlag_Material);
    for (u16 joint = 0; joint < blurData->getJointNum(); joint++)
      for (auto* material = blurData->getJointNodePointer(joint)->getMesh(); material; material = material->getNext()) {
        if (joint == shown) material->getShape()->show();
        else material->getShape()->hide();
      }
    mDoExt_modelUpdateDL(blur);
  };
  return {{"body-stock", body},
          {"green-with-shield", [=] { morf->calc(); morf->entryDL(green); mDoExt_modelUpdateDL(shield); }},
          {"pink-with-telescope", [=] { morf->calc(); morf->entryDL(pink); mDoExt_modelUpdateDL(telescope); }},
          {"body-frozen", [=] { morf->calc(); dMat_control_c::icePlay(); dMat_control_c::iceEntryDL(morf, -1, nullptr); }},
          {"body-restored", body},
          {"blur-club-first", [=] { blurDraw(club, BK_KB_JNT_BLURA_e); }},
          {"blur-club-second", [=] { blurDraw(club, BK_KB_JNT_BLURB_e); }},
          {"blur-sword-first", [=] { blurDraw(sword, BK_KB_JNT_BLURA_e); }},
          {"blur-sword-second", [=] { blurDraw(sword, BK_KB_JNT_BLURB_e); }}};
}

// daCC_Draw body, stone-covered, puddle, breakup and freeze branches. Like the
// actor, the frozen branch keeps the body BRK entered and returns without removal.
static std::vector<ActorState> chuchu_states() {
  auto* body = actor_morf("CC", dRes_INDEX_CC_BMD_CC_e, 0, 0x11020203);
  auto* rock = actor_morf("CC", dRes_INDEX_CC_BDL_CC_IWA_e, 0, 0x11020203);
  auto* puddle = actor_morf("CC", dRes_INDEX_CC_BDL_CC_BETA_e, 0, 0x11020203);
  auto* breakup = actor_morf("CC", dRes_INDEX_CC_BDL_CC_PTCL_e, 0, 0x11020203);
  auto* bodyData = body->getModel()->getModelData();
  auto* rockData = rock->getModel()->getModelData();
  auto* puddleData = puddle->getModel()->getModelData();
  auto* bodyColor = actor_brk(bodyData, "CC", dRes_INDEX_CC_BRK_CC_e);
  auto* rockColorA = actor_brk(rockData, "CC", dRes_INDEX_CC_BRK_CC_IWA01_e);
  auto* rockColorB = actor_brk(rockData, "CC", dRes_INDEX_CC_BRK_CC_IWA02_e);
  auto* rockScrollA = actor_btk(rockData, "CC", dRes_INDEX_CC_BTK_CC_IWA01_e);
  auto* rockScrollB = actor_btk(rockData, "CC", dRes_INDEX_CC_BTK_CC_IWA02_e);
  auto* puddleColor = actor_brk(puddleData, "CC", dRes_INDEX_CC_BRK_CC_BETA_e);
  auto* mask = new mDoExt_invisibleModel();
  check(mask->create(body->getModel()), "create invisible packets");
  const auto bodyDraw = [=] { body->calc(); bodyColor->entry(bodyData); body->entryDL(); bodyColor->remove(bodyData); };
  const auto rockDraw = [=](mDoExt_brkAnm* color, mDoExt_btkAnm* scroll) {
    bodyDraw();
    rock->calc(); color->entry(rockData); scroll->entry(rockData); rock->updateDL();
    color->remove(rockData); scroll->remove(rockData);
  };
  return {{"body", bodyDraw},
          {"stone-first", [=] { rockDraw(rockColorA, rockScrollA); }},
          {"stone-second", [=] { rockDraw(rockColorB, rockScrollB); }},
          {"puddle", [=] { puddle->calc(); puddleColor->entry(puddleData); puddle->updateDL(); puddleColor->remove(puddleData); }},
          {"breakup", [=] { breakup->calc(); bodyColor->entry(bodyData); breakup->updateDL(); bodyColor->remove(bodyData); }},
          {"frozen", [=] {
             body->calc(); bodyColor->entry(bodyData); dMat_control_c::icePlay();
             dMat_control_c::iceUpdateDL(body, -1, mask);
           }}};
}

// daPH_Draw: frozen body/propeller, each with its depth-only invisible packets.
static std::vector<ActorState> peahat_states() {
  auto* body = actor_morf("PH", dRes_INDEX_PH_BDL_PHB_e, 0x80000, 0x37441422);
  auto* propeller = actor_morf("PH", dRes_INDEX_PH_BDL_PHP_e, 0x80000, 0x37441422);
  auto* bodyMask = new mDoExt_invisibleModel();
  auto* propellerMask = new mDoExt_invisibleModel();
  check(bodyMask->create(body->getModel()) && propellerMask->create(propeller->getModel()), "create invisible packets");
  const auto stock = [=] { body->calc(); propeller->calc(); body->entryDL(); propeller->entryDL(); };
  return {{"stock", stock},
          {"frozen", [=] {
             body->calc(); propeller->calc(); dMat_control_c::icePlay();
             dMat_control_c::iceEntryDL(body, -1, bodyMask);
             dMat_control_c::iceEntryDL(propeller, -1, propellerMask);
           }},
          {"restored", stock}};
}

// bpw body_draw, torituki_draw and kantera_draw model paths. The lantern's and
// damage ball's dDlst_alphaModel spheres remain a gap.
static std::vector<ActorState> jalhalla_states() {
  auto* body = actor_morf("BPW", dRes_INDEX_BPW_BDL_BPW_e, 0x80000, 0x37441422);
  auto* possessing = actor_morf("BPW", dRes_INDEX_BPW_BDL_BPW_e, 0x80000, 0x37441422);
  auto* lantern = actor_morf("BPW", dRes_INDEX_BPW_BDL_BPW_KAN1_e, 0x80000, 0x37441422);
  auto* data = body->getModel()->getModelData();
  auto* lanternData = lantern->getModel()->getModelData();
  auto* mask = new mDoExt_invisibleModel();
  auto* possessionMask = new mDoExt_invisibleModel();
  check(mask->create(body->getModel()) && possessionMask->create(possessing->getModel()), "create invisible packets");
  auto* normal = actor_brk(data, "BPW", dRes_INDEX_BPW_BRK_DEFAULT_e, J3DFrameCtrl::EMode_LOOP);
  auto* stun = actor_brk(data, "BPW", dRes_INDEX_BPW_BRK_HIT_e, J3DFrameCtrl::EMode_LOOP);
  auto* curseStart = actor_brk(data, "BPW", dRes_INDEX_BPW_BRK_NOROI_S1_e);
  auto* curseEnd = actor_brk(data, "BPW", dRes_INDEX_BPW_BRK_NOROI_E1_e);
  auto* lightFreeze = actor_brk(data, "BPW", dRes_INDEX_BPW_BRK_HIRARU1_e);
  auto* lanternGlow = actor_brk(lanternData, "BPW", dRes_INDEX_BPW_BRK_BPW_KAN1_e, J3DFrameCtrl::EMode_LOOP);
  const auto opaque = [=] {
    for (u16 i = 0; i < data->getMaterialNum(); i++) data->getMaterialNodePointer(i)->getTevKColor(3)->mColor.a = 255;
  };
  const auto bodyDraw = [=](mDoExt_brkAnm* color, bool frozen) {
    body->calc();
    opaque();
    if (!frozen) dComIfGd_setListMaskOff();
    color->entry(data);
    body->entryDL();
    dComIfGd_setList();
    if (frozen) mask->entry(); else mask->entryMaskOff();
    color->remove(data);
  };
  return {{"default", [=] { bodyDraw(normal, false); }},
          {"light-stun", [=] { bodyDraw(stun, false); }},
          {"curse-start", [=] { bodyDraw(curseStart, false); }},
          {"curse-end", [=] { bodyDraw(curseEnd, false); }},
          {"light-freeze", [=] { bodyDraw(lightFreeze, true); }},
          {"possession", [=] {
             possessing->calc();
             opaque();
             dComIfGd_setListMaskOff();
             possessing->updateDL();
             dComIfGd_setList();
             possessionMask->entryMaskOff();
           }},
          {"lantern", [=] {
             lantern->calc(); lanternGlow->entry(lanternData); lantern->entryDL(); lanternGlow->remove(lanternData);
           }},
          {"default-repeated", [=] { bodyDraw(normal, false); }}};
}

// daBtd_Draw phases and the defeat branch's material-table replacement.
static std::vector<ActorState> gohma_states() {
  auto* first = actor_morf("Btd", dRes_INDEX_BTD_BMD_BTD_e, 0, 0x11020203);
  auto* second = actor_morf("Btd", dRes_INDEX_BTD_BMD_SOTAI_e, 0, 0x11020203);
  auto* firstData = first->getModel()->getModelData();
  auto* secondData = second->getModel()->getModelData();
  auto* firstScroll = actor_btk(firstData, "Btd", dRes_INDEX_BTD_BTK_BTD_e, J3DFrameCtrl::EMode_LOOP);
  auto* firstColor = actor_brk(firstData, "Btd", dRes_INDEX_BTD_BRK_BTD_e, J3DFrameCtrl::EMode_LOOP);
  auto* defeat = (J3DMaterialTable*)dComIfG_getObjectRes("Btd", dRes_INDEX_BTD_BMT_DEADA_e);
  auto* defeatColor = (J3DAnmTevRegKey*)dComIfG_getObjectRes("Btd", dRes_INDEX_BTD_BRK_DEADA_e);
  auto* defeatScroll = (J3DAnmTextureSRTKey*)dComIfG_getObjectRes("Btd", dRes_INDEX_BTD_BTK_DEADA_e);
  // useHeapInit sizes both animations for the larger defeat data, then rebinds.
  auto* secondScroll = actor_btk(secondData, "Btd", dRes_INDEX_BTD_BTK_DEADA_e);
  auto* secondColor = actor_brk(secondData, "Btd", dRes_INDEX_BTD_BRK_DEADA_e);
  check(secondScroll->init(secondData, (J3DAnmTextureSRTKey*)dComIfG_getObjectRes("Btd", dRes_INDEX_BTD_BTK_SOTAI_e),
                           true, J3DFrameCtrl::EMode_LOOP, 1.0f, 0, -1, true, 0)
        && secondColor->init(secondData, (J3DAnmTevRegKey*)dComIfG_getObjectRes("Btd", dRes_INDEX_BTD_BRK_SOTAI_e),
                             true, J3DFrameCtrl::EMode_LOOP, 1.0f, 0, -1, true, 0), "bind second phase animations");
  const auto secondDraw = [=] {
    second->calc(); secondScroll->entry(secondData); secondColor->entry(secondData); second->entryDL();
  };
  return {{"phase-one", [=] { first->calc(); firstScroll->entry(firstData); firstColor->entry(firstData); first->entryDL(); }},
          {"phase-two", secondDraw},
          {"defeat", [=] {
             secondData->setMaterialTable(defeat, J3DMatCopyFlag_Material);
             check(secondColor->init(secondData, defeatColor, true, J3DFrameCtrl::EMode_NONE, 1.0f, 0, -1, true, 0)
                   && secondScroll->init(secondData, defeatScroll, true, J3DFrameCtrl::EMode_NONE, 1.0f, 0, -1, true, 0),
                   "bind defeat animations");
             secondDraw();
           }}};
}

// bgn water0_disp/water1_disp mutate one shared material's blend and depth
// update before drawing into the sky lists.
static std::vector<ActorState> puppet_ganon_states() {
  auto* data = (J3DModelData*)dComIfG_getObjectRes("Bgn", dRes_INDEX_BGN_BDL_R0E_A_e);
  auto* surface = mDoExt_J3DModel__create(data, 0x80000, 0x31000000);
  auto* mask = mDoExt_J3DModel__create(data, 0x80000, 0x30000000);
  check(surface && mask, "create water models");
  auto* material = data->getMaterialNodePointer(0);
  const auto surfaceDraw = [=] {
    dComIfGd_setListSky();
    auto* blend = material->getBlend();
    blend->setType(GX_BM_BLEND);
    blend->setSrcFactor(GX_BL_SRC_ALPHA);
    blend->setDstFactor(GX_BL_INV_SRC_ALPHA);
    material->getZMode()->setUpdateEnable(1);
    mDoExt_modelUpdateDL(surface);
    dComIfGd_setList();
  };
  const auto maskDraw = [=] {
    dComIfGd_setListSky();
    material->getBlend()->setType(GX_BM_NONE);
    material->getZMode()->setUpdateEnable(0);
    mDoExt_modelUpdateDL(mask);
    dComIfGd_setList();
  };
  return {{"water-surface", surfaceDraw}, {"water-mask", maskDraw},
          {"water-combined", [=] { surfaceDraw(); maskDraw(); }}};
}

static const ActorRecipe actorRecipes[] = {
  {"enemy-bokoblin-materials-v1", "/res/Object/Bk.arc:bdlm/bk.bdl", "Bk", bokoblin_states},
  {"enemy-chuchu-states-v1", "/res/Object/Cc.arc:bmdm/cc.bmd", "CC", chuchu_states},
  {"enemy-peahat-freeze-v1", "/res/Object/Ph.arc:bdlm/phb.bdl", "PH", peahat_states},
  {"boss-jalhalla-visibility-v1", "/res/Object/Bpw.arc:bdlm/bpw.bdl", "BPW", jalhalla_states},
  {"boss-gohma-defeat-v1", "/res/Object/Btd.arc:bmdm/sotai.bmd", "Btd", gohma_states},
  {"boss-puppet-ganon-water-v1", "/res/Object/Bgn.arc:bdlm/r0e_a.bdl", "Bgn", puppet_ganon_states},
};

static unsigned draw_actor_states(const std::vector<ActorState>& states) {
  unsigned draws = 0;
  for (unsigned index = 0; index < states.size(); ++index) {
    effectSteps.push_back({index, index + 1, 0, 0});
    activeStep = &effectSteps.back();
    begin_draw();
    dComIfGd_reset();
    states[index].entry();
    // mDoGph_Painter's order for the lists these recipes populate.
    dComIfGd_drawOpaListSky(); dComIfGd_drawXluListSky();
    dComIfGd_drawOpaList(); dComIfGd_drawXluList();
    dComIfGd_drawOpaListMaskOff(); dComIfGd_drawXluListMaskOff();
    activeStep->draws = end_draw();
    check(activeStep->draws && activeStep->lookups, "each actor state must actually draw");
    draws += activeStep->draws;
    activeStep = nullptr;
  }
  return draws;
}

static void write_state_steps(FILE* report, const std::vector<const char*>& names) {
  for (size_t i = 0; i < effectSteps.size(); ++i) {
    const auto& step = effectSteps[i];
    fprintf(report, "%s{\"tick\":%u,\"state\":\"%s\",\"draw_calls\":%u,\"pipeline_lookups\":%u,\"configurations\":[",
            i ? "," : "", step.tick, names[step.variant], step.draws, step.lookups);
    for (size_t k = 0; k < step.configurations.size(); ++k)
      fprintf(report, "%s{\"type\":1,\"hash\":%lld}", k ? "," : "", static_cast<long long>(step.configurations[k]));
    fprintf(report, "]}");
  }
}

#include "scene-collector.hpp"
namespace pc { void loadAssets(); }

int main(int argc, char* argv[]) {
  check(argc >= 3 && argc <= 5, "usage: collector IMAGE BASELINE_ASSETS [SCENARIO [RESOURCE]] (new private directory)");
  const bool bombNormal = argc == 5 && !strcmp(argv[3], "equipment-bomb-normal-v1");
  const bool bombCheap = argc == 5 && !strcmp(argv[3], "equipment-bomb-cheap-v1");
  const bool arrow = argc == 5 && !strcmp(argv[3], "equipment-arrow-tips-v1");
  const bool deathLarge = argc == 5 && !strcmp(argv[3], "enemy-death-large-v1");
  const bool deathSmall = argc == 5 && !strcmp(argv[3], "enemy-death-small-v1");
  const bool particles = bombNormal || bombCheap || deathLarge || deathSmall
                         || (argc == 5 && !strcmp(argv[3], "particle-effect-lifecycle-v1"));
  const bool dynamic = particles || (argc == 4 && !strcmp(argv[3], "common-pot-debris-lifecycle-v1"));
  const bool inventory = argc == 5 && !strcmp(argv[3], "asset-model-stock-v1");
  const bool scene = argc == 5 && (!strcmp(argv[3], "scene-ocean-world-v1")
                     || !strcmp(argv[3], "scene-simple-shadows-v1") || !strcmp(argv[3], "scene-alpha-overlap-v1"));
  const ActorRecipe* actor = nullptr;
  for (const auto& recipe : actorRecipes)
    if (argc == 5 && !strcmp(argv[3], recipe.scenario)) actor = &recipe;
  check(argc == 3 || dynamic || inventory || arrow || actor || scene || (argc == 4 && !strcmp(argv[3], "always-small-pot-stock-v1")),
        "unknown scenario");
  const std::string resource = inventory || particles || arrow || actor || scene ? argv[4] : "/res/Object/Always.arc:bdl/obm_kotubo1.bdl";
  check(!scene || resource == "/res/Object/Always.arc", "fixed scene resource required");
  check(!arrow || resource == "/res/Object/Link.arc:bdlm/arrow.bdl", "fixed arrow resource required");
  check(!actor || resource == actor->resource, "fixed actor resource required");
  check(!bombNormal || resource == "/res/Particle/common.jpc:0x000b+0x2009+0x200a+0x2008", "normal bomb recipe");
  check(!bombCheap || resource == "/res/Particle/common.jpc:0x000b+0x232a+0x200a+0x2008", "cheap bomb recipe");
  check(!deathLarge || resource == "/res/Particle/common.jpc:0x0014+0x0013+0x0015+0x0016", "large enemy death recipe");
  check(!deathSmall || resource == "/res/Particle/common.jpc:0x043c+0x043d+0x043e", "small enemy death recipe");
  const auto particleIds = particles ? particle_ids(resource, deathLarge || deathSmall) : std::vector<unsigned>{};
  const auto modelResource = particles || actor || scene ? std::string("/res/Object/Always.arc:bdl/obm_kotubo1.bdl") : resource;
  const auto separator = modelResource.find(':');
  check(separator != std::string::npos && modelResource.find(':', separator + 1) == std::string::npos,
        "one archive/member separator required");
  const auto archivePath = modelResource.substr(0, separator);
  const auto memberPath = modelResource.substr(separator + 1);
  check(archivePath.starts_with("/res/") && archivePath.ends_with(".arc") && memberPath.ends_with(".bdl")
        && modelResource.find("..") == std::string::npos && !memberPath.starts_with('/')
        && std::all_of(modelResource.begin(), modelResource.end(), [](unsigned char c) {
          return std::isalnum(c) || c == '/' || c == '.' || c == '_' || c == '-' || c == ':';
        }), "supported stock BDL resource path required");
  const auto runtimeIdentityRows = verify_runtime_identities(argv[2]);
  check(!std::filesystem::exists("observed.db") && !std::filesystem::exists("cache"), "retain earlier output");
  check(sqlite3_open("observed.db", &observed) == SQLITE_OK, "open observations");
  check(sqlite3_exec(observed, "CREATE TABLE aurora_schema(value INTEGER); INSERT INTO aurora_schema VALUES(1);"
    "CREATE TABLE pipeline_cache(type INTEGER, hash INTEGER, config_version INTEGER, config_size INTEGER,"
    "config BLOB, first_frame_used INTEGER, PRIMARY KEY(type,hash));", nullptr, nullptr, nullptr) == SQLITE_OK,
    "observation schema");
  std::filesystem::create_directory("cache");
  AuroraConfig config{};
  config.appName = "PSWaker model collector";
  config.resourcesPath = argv[2]; config.userPath = "."; config.cachePath = "cache";
  config.desiredBackend = BACKEND_VULKAN; config.allowCpuAdapter = true;
  config.windowWidth = 1280; config.windowHeight = 720; config.msaa = 1;
  config.mem1Size = 256 * 1024 * 1024; config.mem2Size = 16 * 1024 * 1024;
  config.blockingPipelines = true;
  const auto info = aurora_initialize(argc, argv, &config);
  check(info.window && info.backend == BACKEND_VULKAN, "initialize selected Vulkan renderer");
  const auto preparationScene = aurora::gfx::scene_render_target_layout();
  auto preparationOffscreen = preparationScene;
  preparationOffscreen.colorAttachmentCount = 1;
  preparationOffscreen.sampleCount = 1;
  aurora::gfx::detail::finalize_render_target_layout(preparationOffscreen);
  VISetFrameBufferScale(1.5f);
  AuroraSetFitAspect(16.0f / 9.0f);
  check(aurora_dvd_open(argv[1]), "open supported disc");
  const auto* disc = DVDGetCurrentDiskID();
  check(disc && !memcmp(disc->gameName, "GZLE", 4) && !memcmp(disc->company, "01", 2)
        && disc->gameVersion == 0, "GZLE01 revision 0 required");
  // Scene packets consume disc-backed constant display lists/vertices. Follow
  // pc_main's validated runtime-asset loading before any game code uses them.
  if (scene) pc::loadAssets();
  OSInit();
  GXInit(nullptr, 0);
  GXSetPixelFmt(GX_PF_RGB8_Z24, GX_ZC_LINEAR);
  VIConfigure(&GXNtsc480IntDf);
  check(JKRExpHeap::createRoot(64, false), "create isolated game heap");
  check(JMANewSinTable(12), "initialize the game's transform tables as mDoMch_Create does");
  J3DModel* model = nullptr;
  unsigned materials = 0;
  std::vector<ActorState> actorStates;
  if (scene) {
    create_actor_runtime();
    mDoGph_gInf_c::createHeap();
    actorStates = scene_states(argv[3]);
  } else if (actor) {
    create_actor_runtime();
    load_object(actor->archive);
    // fopAcM_entrySolidHeap: animation binding requires an actor's solid heap.
    check(mDoExt_createSolidHeapFromGameToCurrent(0x1000000, 0), "create actor heap");
    actorStates = actor->states();
    mDoExt_restoreCurrentHeap();
  } else if (!dynamic) {
    auto* archive = JKRArchive::mount(archivePath.c_str(), JKRArchive::MOUNT_MEM,
                                   JKRHeap::getCurrentHeap(), JKRArchive::MOUNT_DIRECTION_HEAD);
    check(archive, "mount model archive through game loader");
    auto* bytes = archive->getResource(memberPath.c_str());
    check(bytes, "find requested stock model");
    auto* data = J3DModelLoaderDataBase::loadBinaryDisplayList(bytes, 0x2020);
    check(data && data->getMaterialNum() > 0 && (inventory || arrow || data->getMaterialNum() == 1),
          "load supported stock model materials");
    materials = data->getMaterialNum();
    model = mDoExt_J3DModel__create(data, arrow ? 0x00080000 : 0, arrow ? 0x11000022 : 0x11000084);
    check(model, "create game model and material display lists");
  }
  J3DDrawBuffer opaque(32), translucent(32);
  j3dSys.setDrawBuffer(&opaque, J3DSysDrawBuf_Opa);
  j3dSys.setDrawBuffer(&translucent, J3DSysDrawBuf_Xlu);
  Mtx view;
  MTXIdentity(view); view[2][3] = -200;
  j3dSys.setViewMtx(view);
  const auto deadline = pswaker_perf_now() + 120000000000ull;
  while (!aurora::gfx::pipeline_preparation_status().complete) {
    check(!aurora::gfx::pipeline_preparation_status().error && pswaker_perf_now() < deadline, "baseline preparation");
    aurora_update();
    if (aurora_begin_frame()) aurora_end_frame();
  }
  check(aurora::gfx::finish_pipeline_preparation(), "finish preparation");
  recording = true;
  unsigned renderedDraws = 0;
  if (dynamic) {
    const auto setup = deathLarge || deathSmall ? ParticleSetup::EnemyDeath
                       : bombCheap ? ParticleSetup::CheapBomb : ParticleSetup::Plain;
    renderedDraws = particles ? draw_particles(view, particleIds, setup) : draw_effect(view);
  } else if (scene) {
    renderedDraws = draw_scene_states(actorStates);
  } else if (actor) {
    renderedDraws = draw_actor_states(actorStates);
  } else if (arrow) {
    // daArrow_c::createInit/_draw: hide all tip shapes, show the selected
    // material and its optional next material for drawing, then hide again.
    // Player attachment, BTK animation and elemental actors are separate gaps.
    auto* data = model->getModelData();
    check(data->getJointNum() > ARROW_JNT_TIPNOMAL_e, "arrow tip joints required");
    const unsigned tips[] = {ARROW_JNT_TIPNOMAL_e, ARROW_JNT_TIPFIRE_e, ARROW_JNT_TIPICE_e};
    for (const auto joint : tips) {
      auto* material = data->getJointNodePointer(joint)->getMesh();
      check(material && material->getShape(), "arrow tip material required");
      material->getShape()->hide();
      if (material->getNext()) material->getNext()->getShape()->hide();
    }
    const unsigned cycle[] = {0, 1, 2, 0};
    for (unsigned tick = 0; tick < 4; ++tick) {
      auto* material = data->getJointNodePointer(tips[cycle[tick]])->getMesh();
      material->getShape()->show();
      if (material->getNext()) material->getNext()->getShape()->show();
      effectSteps.push_back({cycle[tick], tick + 1, 0, 0});
      activeStep = &effectSteps.back();
      begin_draw();
      opaque.frameInit(); translucent.frameInit();
      model->update(); model->viewCalc();
      j3dSys.setDrawModeOpaTexEdge(); opaque.draw();
      j3dSys.setDrawModeXlu(); translucent.draw();
      activeStep->draws = end_draw();
      check(activeStep->draws && activeStep->lookups, "each arrow state must actually draw");
      renderedDraws += activeStep->draws;
      activeStep = nullptr;
      material->getShape()->hide();
      if (material->getNext()) material->getNext()->getShape()->hide();
    }
  } else {
    for (int frame = 0; frame < 3; ++frame) {
      begin_draw();
      opaque.frameInit(); translucent.frameInit();
      model->update(); model->viewCalc();
      j3dSys.setDrawModeOpaTexEdge(); opaque.draw();
      j3dSys.setDrawModeXlu(); translucent.draw();
      renderedDraws += end_draw();
    }
  }
  recording = false;
  aurora_shutdown(); // Join render work and close the normal recorder before export.
  check(drawCalls > 0 && renderedDraws > 0, "real GX material draws required");
  const auto& target = observedLayout.colorAttachments[0];
  check(target.width == 1280 && target.height == 720 && observedLayout.sampleCount == 1,
        "selected PS4 target settings required");
  check(sqlite3_close(observed) == SQLITE_OK, "close observation database");
  auto* report = fopen("collection.json", "wx");
  check(report, "new collection report");
  if (scene) {
    write_scene_report(report, argv[3], actorStates, renderedDraws, runtimeIdentityRows,
                       preparationScene, preparationOffscreen);
  } else if (particles) {
    fprintf(report, "{\"schema\":1,\"scenario\":\"%s\",\"method\":\"dynamic-effect-draw\","
            "\"resource\":\"%s\",\"draw_calls\":%u,\"pipeline_lookups\":%u,\"runtime_identity_verified_rows\":%u,"
            "\"frames\":%zu,\"script\":{\"effect_ids\":[", argv[3], resource.c_str(), renderedDraws, drawCalls,
            runtimeIdentityRows, effectSteps.size());
    for (size_t i = 0; i < particleIds.size(); ++i) fprintf(report, "%s%u", i ? "," : "", particleIds[i]);
    fprintf(report, "],\"max_ticks\":240,\"continuous_emission_ticks\":30,\"variations\":["
            "{\"random_seed\":0,\"scale\":1,\"alpha\":255,\"texture_index\":0},"
            "{\"random_seed\":1,\"scale\":2,\"alpha\":128,\"texture_index\":1}]");
    if (bombNormal || bombCheap) fprintf(report, ",\"setup\":\"%s\"", bombCheap ? "cheap-bomb-v1" : "normal-bomb-v1");
    if (deathLarge || deathSmall) fprintf(report, ",\"setup\":\"%s\"", argv[3]);
    fprintf(report, "},"
            "\"unhandled_states\":[\"stage-lighting-and-wind\",\"projection-framebuffer\","
            "\"model-particles\",\"actor-collision\",\"other-cameras\"]");
    write_effect_steps(report);
  } else if (actor) {
    std::vector<const char*> names;
    for (const auto& state : actorStates) names.push_back(state.name);
    fprintf(report, "{\"schema\":1,\"scenario\":\"%s\",\"method\":\"scripted-actor-draw\",\"resource\":\"%s\","
            "\"draw_calls\":%u,\"pipeline_lookups\":%u,\"runtime_identity_verified_rows\":%u,\"frames\":%zu,"
            "\"script\":{\"states\":[", actor->scenario, resource.c_str(), renderedDraws, drawCalls,
            runtimeIdentityRows, names.size());
    for (size_t i = 0; i < names.size(); ++i) fprintf(report, "%s\"%s\"", i ? "," : "", names[i]);
    fprintf(report, "],\"frames_per_state\":1},"
            "\"unhandled_states\":[\"actor-process-and-ai\",\"skeletal-animation\",\"stage-lighting-and-fog\","
            "\"shadows\",\"other-cameras\"],\"states\":[");
    write_state_steps(report, names);
    fprintf(report, "]");
  } else if (arrow) {
    fprintf(report, "{\"schema\":1,\"scenario\":\"equipment-arrow-tips-v1\",\"method\":\"scripted-equipment-draw\","
            "\"resource\":\"%s\",\"materials\":%u,\"draw_calls\":%u,\"pipeline_lookups\":%u,"
            "\"runtime_identity_verified_rows\":%u,\"frames\":4,"
            "\"script\":{\"states\":[\"normal\",\"fire\",\"ice\",\"normal\"],\"frames_per_state\":1,"
            "\"loader_flags\":8224,\"model_flags\":524288,\"differed_display_list_flags\":285212706},"
            "\"unhandled_states\":[\"texture-animation\",\"elemental-effects-and-trails\",\"actor-lighting-and-collision\","
            "\"player-attachment-and-flight\",\"light-arrow\",\"other-cameras\"],\"states\":[",
            resource.c_str(), materials, renderedDraws, drawCalls, runtimeIdentityRows);
    write_state_steps(report, {"normal", "fire", "ice"});
    fprintf(report, "]");
  } else if (dynamic) {
    fprintf(report, "{\"schema\":1,\"scenario\":\"common-pot-debris-lifecycle-v1\","
            "\"method\":\"dynamic-effect-draw\",\"resource\":\"/res/Particle/common.jpc:0x0018\","
            "\"draw_calls\":%u,\"pipeline_lookups\":%u,\"runtime_identity_verified_rows\":%u,\"frames\":%zu,"
            "\"script\":{\"effect_id\":24,\"random_seed\":0,\"max_ticks\":180,\"position\":[0,0,0],"
            "\"scale\":[1,1,1],\"color\":[255,255,255,255],\"texture_indices\":[0,1]},"
            "\"unhandled_states\":[\"model-shards-0x0017\",\"actor-lighting-and-collision\","
            "\"other-pot-textures\",\"overlapping-effects\",\"other-cameras\"]",
            renderedDraws, drawCalls, runtimeIdentityRows, effectSteps.size());
    write_effect_steps(report);
  } else fprintf(report, "{\"schema\":1,\"scenario\":\"%s\","
    "\"method\":\"asset-material-draw\",\"resource\":\"%s\","
    "\"materials\":%u,\"draw_calls\":%u,\"pipeline_lookups\":%u,\"runtime_identity_verified_rows\":%u,"
    "\"frames\":3,\"loader_flags\":8224,"
    "\"model_flags\":0,\"differed_display_list_flags\":285212804",
    inventory ? "asset-model-stock-v1" : "always-small-pot-stock-v1", resource.c_str(), materials,
    renderedDraws, drawCalls, runtimeIdentityRows);
  fprintf(report, ",\"layout\":{\"key\":%llu,\"attachments\":%u,\"color_format\":%u,\"depth_format\":%u,"
    "\"samples\":%u,\"width\":%u,\"height\":%u}}\n",
    static_cast<unsigned long long>(observedLayout.key), observedLayout.colorAttachmentCount,
    static_cast<uint32_t>(target.format), static_cast<uint32_t>(observedLayout.depthStencilFormat),
    observedLayout.sampleCount, target.width, target.height);
  check(fclose(report) == 0, "write collection report");
  // The linked game's global destructors assume a fully booted game (pads,
  // actors, audio). This asset-only process never starts those systems. GPU
  // workers, both recorders and the report have already been closed explicitly.
  fflush(nullptr);
  std::_Exit(0);
}
