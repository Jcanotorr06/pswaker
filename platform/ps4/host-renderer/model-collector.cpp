// Maintainer-only asset draw. Linked to the same prepared game and GX renderer
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
#include "JSystem/JMath/JMath.h"
#include "JSystem/J3DGraphLoader/J3DModelLoader.h"
#include "JSystem/J3DGraphAnimator/J3DModel.h"
#include "JSystem/J3DGraphAnimator/J3DModelData.h"
#include "JSystem/J3DGraphBase/J3DDrawBuffer.h"
#include "m_Do/m_Do_ext.h"
#include "gx/pipeline.hpp"
#include "gfx/resources.hpp"
#include "frame-pacing.hpp"
#include <sqlite3.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <mutex>

static sqlite3* observed;
static std::mutex observationMutex;
static unsigned drawCalls;
static aurora::gfx::RenderTargetLayout observedLayout;
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

int main(int argc, char* argv[]) {
  check(argc == 3, "usage: collector IMAGE BASELINE_ASSETS (run in a new private directory)");
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
  VISetFrameBufferScale(1.5f);
  AuroraSetFitAspect(16.0f / 9.0f);
  check(aurora_dvd_open(argv[1]), "open supported disc");
  const auto* disc = DVDGetCurrentDiskID();
  check(disc && !memcmp(disc->gameName, "GZLE", 4) && !memcmp(disc->company, "01", 2)
        && disc->gameVersion == 0, "GZLE01 revision 0 required");
  OSInit();
  GXInit(nullptr, 0);
  GXSetPixelFmt(GX_PF_RGB8_Z24, GX_ZC_LINEAR);
  VIConfigure(&GXNtsc480IntDf);
  check(JKRExpHeap::createRoot(64, false), "create isolated game heap");
  check(JMANewSinTable(12), "initialize the game's transform tables as mDoMch_Create does");
  auto* archive = JKRArchive::mount("/res/Object/Always.arc", JKRArchive::MOUNT_MEM,
                                   JKRHeap::getCurrentHeap(), JKRArchive::MOUNT_DIRECTION_HEAD);
  check(archive, "mount Always archive through game loader");
  auto* bytes = archive->getResource("bdl/obm_kotubo1.bdl");
  check(bytes, "find small pot model");
  auto* data = J3DModelLoaderDataBase::loadBinaryDisplayList(bytes, 0x2020);
  check(data && data->getMaterialNum() == 1, "load the fixed one-material model");
  auto* model = mDoExt_J3DModel__create(data, 0, 0x11000084);
  check(model, "create game model and material display lists");
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
  unsigned renderedDraws = 0;
  for (int frame = 0; frame < 3; ++frame) {
    aurora_update();
    check(aurora_begin_frame(), "begin model frame");
    GXSetViewport(0, 0, 640, 480, 0, 1);
    GXSetScissor(0, 0, 640, 480);
    Mtx44 projection;
    MTXPerspective(projection, 45, 4.0f / 3.0f, 1, 10000);
    GXSetProjection(projection, GX_PERSPECTIVE);
    j3dSys.drawInit();
    opaque.frameInit(); translucent.frameInit();
    model->update(); model->viewCalc();
    j3dSys.setDrawModeOpaTexEdge(); opaque.draw();
    j3dSys.setDrawModeXlu(); translucent.draw();
    aurora_end_frame();
    aurora::gfx::synchronize();
    renderedDraws += aurora_get_stats()->drawCallCount;
  }
  aurora_shutdown(); // Join render work and close the normal recorder before export.
  check(drawCalls > 0 && renderedDraws > 0, "real GX material draws required");
  const auto& target = observedLayout.colorAttachments[0];
  check(target.width == 1280 && target.height == 720 && observedLayout.sampleCount == 1,
        "selected PS4 target settings required");
  check(sqlite3_close(observed) == SQLITE_OK, "close observation database");
  auto* report = fopen("collection.json", "wx");
  check(report, "new collection report");
  fprintf(report, "{\"schema\":1,\"scenario\":\"always-small-pot-stock-v1\","
    "\"method\":\"asset-material-draw\",\"resource\":\"/res/Object/Always.arc:bdl/obm_kotubo1.bdl\","
    "\"materials\":1,\"draw_calls\":%u,\"pipeline_lookups\":%u,\"runtime_identity_verified_rows\":%u,"
    "\"frames\":3,\"loader_flags\":8224,"
    "\"model_flags\":0,\"differed_display_list_flags\":285212804,"
    "\"layout\":{\"key\":%llu,\"attachments\":%u,\"color_format\":%u,\"depth_format\":%u,"
    "\"samples\":%u,\"width\":%u,\"height\":%u}}\n", renderedDraws, drawCalls, runtimeIdentityRows,
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
