#include "resource-evidence.hpp"
#include <cstddef>
#include <cstdint>
#include <cstdio>

extern "C" void say(const char*, ...) __attribute__((format(printf, 1, 2)));
extern "C" void ac_ps4_get_memory(uint64_t*, uint64_t*, uint64_t*);
extern "C" size_t pswaker_heap_used();
extern "C" int sceKernelAvailableFlexibleMemorySize(size_t*);

void pswaker_log_resources(const char* phase, double elapsedMs) {
    uint64_t garlic = 0, onion = 0, buffers = 0;
    ac_ps4_get_memory(&garlic, &onion, &buffers);
    size_t flexible = 0;
    const int result = sceKernelAvailableFlexibleMemorySize(&flexible);
    char available[32] = "unavailable";
    if (result == 0) snprintf(available, sizeof available, "%zu", flexible);
    say("RESOURCE ms=%.1f garlic=%llu onion=%llu buffers=%llu main-mspace-allocated=%zu flexible-available=%s query-result=%d phase=%s",
        elapsedMs, (unsigned long long)garlic, (unsigned long long)onion,
        (unsigned long long)buffers, pswaker_heap_used(), available, result, phase);
}
