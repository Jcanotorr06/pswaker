#pragma once
#include <aurora/aurora.h>
// Async FIFO completion is excluded from this checkpoint's renderer contract.
#if defined(__ORBIS__)
#define aurora_get_async_end_frame() 0
#endif

void pswaker_stage(const char* name);
void pswaker_aurora_log(AuroraLogLevel level, const char* module, const char* message, unsigned length);
void pswaker_graphics_ready();
void pswaker_frame_boundary();
[[noreturn]] void pswaker_installation_error(const char* reason);
[[noreturn]] void pswaker_exit(int code);
