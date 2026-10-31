// Renderer startup through Aurora's real initialization/frame API. Only the
// driver boundary is delayed/faulted; the seed, queues and pipelines are real.
#include <aurora/aurora.h>
#include <aurora/gfx.h>
#include <aurora/event.h>
#include "gfx/pipeline_cache.hpp"
#include "gfx/clear.hpp"
#include "gfx/resources.hpp"
#include "frame-pacing.hpp"
#include <sqlite3.h>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <thread>
#include <sys/resource.h>

static std::atomic<bool> hold{true}, entered{false};
static bool failCreation, invalidCreation;
static std::atomic<unsigned> waitCalls{0};
static bool checkProgress;
static std::atomic<unsigned> creations{0}, permits{0};
static std::atomic<unsigned> cacheHits{0};
static WGPUDawnLoadCacheDataCallbackInfo cacheLoader{};
extern "C" WGPUFuture __real_wgpuAdapterRequestDevice(WGPUAdapter, const WGPUDeviceDescriptor*, WGPURequestDeviceCallbackInfo);
extern "C" WGPUFuture __wrap_wgpuAdapterRequestDevice(WGPUAdapter adapter, const WGPUDeviceDescriptor* descriptor,
                                                     WGPURequestDeviceCallbackInfo callback) {
  // Copy the selected Dawn descriptor chain to observe actual driver cache
  // callbacks. Keep all toggles and forward the real renderer cache unchanged.
  auto device = *descriptor;
  WGPUDawnTogglesDescriptor toggles{};
  WGPUDawnCacheDeviceDescriptor cache{};
  auto* chain = device.nextInChain;
  if (chain && chain->sType == WGPUSType_DawnTogglesDescriptor) {
    toggles = *reinterpret_cast<const WGPUDawnTogglesDescriptor*>(chain);
    chain = chain->next;
    device.nextInChain = &toggles.chain;
  }
  if (chain && chain->sType == WGPUSType_DawnCacheDeviceDescriptor) {
    cache = *reinterpret_cast<const WGPUDawnCacheDeviceDescriptor*>(chain);
    cacheLoader = cache.dawnLoadCacheDataCallbackInfo;
    cache.dawnLoadCacheDataCallbackInfo.callback = [](size_t keySize, const uint8_t* key,
        size_t valueSize, uint8_t* value, void*, void*) {
      const auto size = cacheLoader.callback(keySize, key, valueSize, value, cacheLoader.userdata1, cacheLoader.userdata2);
      if (value && size) ++cacheHits;
      return size;
    };
    if (device.nextInChain == &toggles.chain) toggles.chain.next = &cache.chain;
    else device.nextInChain = &cache.chain;
  }
  return __real_wgpuAdapterRequestDevice(adapter, &device, callback);
}
extern "C" WGPURenderPipeline __real_wgpuDeviceCreateRenderPipeline(WGPUDevice, const WGPURenderPipelineDescriptor*);
extern "C" WGPURenderPipeline __wrap_wgpuDeviceCreateRenderPipeline(WGPUDevice device,
                                                                 const WGPURenderPipelineDescriptor* desc) {
  const std::string_view label(desc->label.data, desc->label.length == WGPU_STRLEN ?
                               strlen(desc->label.data) : desc->label.length);
  if (label.starts_with("EFB Clear Pipeline")) {
    entered = true;
    const auto creation = ++creations;
    while (checkProgress && permits < creation) std::this_thread::sleep_for(std::chrono::milliseconds(1));
    while (hold) std::this_thread::sleep_for(std::chrono::milliseconds(1));
    if (failCreation) return nullptr;
    if (invalidCreation) {
      wgpuDeviceInjectError(device, WGPUErrorType_Validation,
                            {"synthetic driver creation error", WGPU_STRLEN});
    }
  }
  return __real_wgpuDeviceCreateRenderPipeline(device, desc);
}
extern "C" uint64_t pswaker_perf_now() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count();
}
extern "C" void pswaker_perf_shader_wait(uint64_t) { ++waitCalls; }
extern "C" PswakerFrameTag pswaker_perf_capture() { return {}; }
extern "C" void pswaker_perf_present(PswakerFrameTag) {}
extern "C" void pswaker_perf_present_failed() {}

static void check(bool pass, const char* name) {
  printf("%s %s\n", pass ? "PASS" : "FAIL", name);
  fflush(stdout);
  if (!pass) std::exit(1);
}
static void seed(const char* mode) {
  if (!strcmp(mode, "missing") || !strcmp(mode, "reuse")) return;
  sqlite3* db = nullptr;
  check(sqlite3_open("initial_pipeline_cache.db", &db) == SQLITE_OK, "seed-open");
  check(sqlite3_exec(db, "CREATE TABLE aurora_schema(value INTEGER); INSERT INTO aurora_schema VALUES(1);"
    "CREATE TABLE pipeline_cache(type INTEGER, hash INTEGER, config_version INTEGER, config_size INTEGER,"
    "config BLOB, first_frame_used INTEGER, PRIMARY KEY(type,hash));", nullptr, nullptr, nullptr) == SQLITE_OK, "seed-schema");
  if (strcmp(mode, "empty")) {
    sqlite3_stmt* stmt = nullptr;
    check(sqlite3_prepare_v2(db, "INSERT INTO pipeline_cache VALUES(0,?,5,8,?,0)", -1, &stmt, nullptr) == SQLITE_OK, "seed-row");
    for (int i = 0; i != 2; ++i) {
      aurora::gfx::clear::PipelineConfig config;
      config.clearDepth = i != 0;
      sqlite3_bind_int(stmt, 1, i);
      sqlite3_bind_blob(stmt, 2, &config, sizeof config, SQLITE_TRANSIENT);
      check(sqlite3_step(stmt) == SQLITE_DONE, "seed-insert");
      sqlite3_reset(stmt);
    }
    sqlite3_finalize(stmt);
  }
  sqlite3_close(db);
  if (!strcmp(mode, "corrupt")) {
    auto* file = fopen("initial_pipeline_cache.db", "wb");
    fputs("corrupt seed", file);
    fclose(file);
  }
  if (!strcmp(mode, "incompatible")) {
    sqlite3_open("initial_pipeline_cache.db", &db);
    sqlite3_exec(db, "UPDATE pipeline_cache SET config_version=999", nullptr, nullptr, nullptr);
    sqlite3_close(db);
  }
}
int main(int argc, char** argv) {
  const rlimit noCore{0, 0};
  setrlimit(RLIMIT_CORE, &noCore);
  const char* mode = argc > 1 ? argv[1] : "cold";
  failCreation = !strcmp(mode, "creation-failure");
  invalidCreation = !strcmp(mode, "validation-failure");
  checkProgress = !strcmp(mode, "progress");
  check(!aurora::gfx::pipeline_preparation_status().complete, "uninitialized-renderer-is-not-complete");
  seed(mode);
  std::filesystem::create_directories("cache");
  AuroraConfig config{};
  config.appName = "Shader startup checks";
  config.resourcesPath = "."; config.userPath = "."; config.cachePath = "cache";
  config.desiredBackend = BACKEND_VULKAN; config.allowCpuAdapter = true;
  config.windowWidth = 1280; config.windowHeight = 720; config.msaa = 1;
  config.blockingPipelines = true;
  const auto info = aurora_initialize(argc, argv, &config);
  check(info.window != nullptr, "renderer-initialized");
  if (!strcmp(mode, "missing") || !strcmp(mode, "empty") || !strcmp(mode, "corrupt") ||
      !strcmp(mode, "incompatible")) {
    const auto status = aurora::gfx::pipeline_preparation_status();
    check(status.error != nullptr && !status.complete, "bad-seed-stops-before-gameplay");
  } else {
    const auto deadline = pswaker_perf_now() + 10000000000ull;
    while (!entered && pswaker_perf_now() < deadline) std::this_thread::sleep_for(std::chrono::milliseconds(1));
    check(entered, "driver-creation-started");
    auto status = aurora::gfx::pipeline_preparation_status();
    check(!status.complete && status.pending > 0 && status.ready == 0, "in-flight-work-is-not-complete");
    check(!aurora::gfx::finish_pipeline_preparation(), "cannot-enter-gameplay-with-pending-work");
    check(status.total >= 2, "seed-configurations-scheduled");
    hold = false;
    if (checkProgress) {
      permits = 1;
      while (creations < 2 && pswaker_perf_now() < deadline) std::this_thread::sleep_for(std::chrono::milliseconds(1));
      status = aurora::gfx::pipeline_preparation_status();
      check(status.ready == 1 && status.pending > 0 && !status.complete,
            "progress-counts-ready-configurations-and-keeps-in-flight-work-pending");
      permits = UINT32_MAX;
    }
    do {
      aurora_update();
      if (aurora_begin_frame()) aurora_end_frame();
      status = aurora::gfx::pipeline_preparation_status();
    } while (!status.complete && !status.error && pswaker_perf_now() < deadline);
    if (failCreation || invalidCreation) check(status.error && !status.complete, "failed-creation-is-not-success");
    else {
      check(status.complete && !status.error && !status.pending && status.ready == status.total,
            "all-included-configurations-ready-before-gameplay");
      check(status.finishedNs >= status.startedNs && status.startedNs != 0, "full-preparation-time-recorded");
      check(aurora::gfx::finish_pipeline_preparation(), "preparation-handoff-to-gameplay");
      printf("DRIVER cache-hits=%u\n", cacheHits.load());
      if (!strcmp(mode, "uncovered") || !strcmp(mode, "runtime-failure") || !strcmp(mode, "runtime-validation-failure")) {
        failCreation = !strcmp(mode, "runtime-failure");
        invalidCreation = !strcmp(mode, "runtime-validation-failure");
        hold = true;
        const auto calls = waitCalls.load();
        std::thread release([] {
          std::this_thread::sleep_for(std::chrono::milliseconds(80));
          hold = false;
        });
        aurora::gfx::clear::PipelineConfig uncovered;
        uncovered.clearColor = false;
        const auto ref = aurora::gfx::find_pipeline(uncovered, aurora::gfx::scene_render_target_layout());
        aurora::gfx::CompiledPipeline pipeline;
        check(aurora::gfx::get_pipeline(ref, pipeline) && pipeline.main && waitCalls > calls,
              "uncovered-configuration-blocks-and-retains-gameplay-wait-accounting");
        release.join();
      }
    }
  }
  hold = false;
  aurora_shutdown();
  return 0;
}
