#pragma once
#include <cstdint>

// Shared by the game thread and Aurora's recording/render workers. UI frames
// carry frame=0. The tag follows the actual present, rather than a CPU heartbeat.
struct PswakerFrameTag { uint64_t frame; unsigned sample; char stage[64]; int room; };
void pswaker_perf_initialize(const char* build, const char* logsRoot = "/data/pswaker/logs");
void pswaker_perf_shutdown();
void pswaker_perf_arm(const char* scene);
void pswaker_perf_game_frame(uint64_t frame);
void pswaker_perf_pause();
void pswaker_perf_phase(const char* phase);
void pswaker_perf_stage(const char* stage, int room);
void pswaker_perf_scene_request(const char* scene);
const char* pswaker_perf_status();
extern "C" PswakerFrameTag pswaker_perf_capture();
extern "C" void pswaker_perf_present(PswakerFrameTag tag);
extern "C" void pswaker_perf_present_failed();
extern "C" uint64_t pswaker_perf_now();
extern "C" void pswaker_perf_shader_wait(uint64_t start);
