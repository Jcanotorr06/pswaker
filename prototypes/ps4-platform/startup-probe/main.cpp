// Startup isolation only. No graphics, audio or controller initialization.
#include <orbis/libkernel.h>
extern "C" void pswaker_startup_stage(const char*);
#define main runtime_preflight_entry
#include "runtime-body.cpp"
#undef main

int main() {
  pswaker_startup_stage("MAIN before selected runtime preflight");
  int result = runtime_preflight_entry();
  pswaker_startup_stage(result == 0 ? "PREFLIGHT PASS" : "PREFLIGHT FAIL");
  pswaker_startup_stage("WAIT 30 seconds; black screen and silence are expected for this probe");
  for (int i = 0; i < 30; ++i) {
    if (sceKernelUsleep(1000000) != 0) {
      pswaker_startup_stage("WAIT failed");
      return 1;
    }
  }
  pswaker_startup_stage("RETURN from main; inspect shell outcome separately");
  return result;
}
