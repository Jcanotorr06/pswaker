#include "resource-evidence.hpp"
#include <cstdarg>
#include <cstddef>
#include <cstdint>
#include <cstdio>

bool failed = false;
extern "C" void say(const char* format, ...) {
    va_list arguments;
    va_start(arguments, format);
    vprintf(format, arguments);
    va_end(arguments);
    putchar('\n');
}
extern "C" void ac_ps4_get_memory(uint64_t* garlic, uint64_t* onion, uint64_t* buffers) {
    *garlic = 1048576;
    *onion = 2097152;
    *buffers = 7;
}
extern "C" size_t pswaker_heap_used() { return 3145728; }
extern "C" int sceKernelAvailableFlexibleMemorySize(size_t* available) {
    *available = 4194304;
    return failed ? -5 : 0;
}
int main(int argc, char**) {
    failed = argc > 1;
    pswaker_log_resources("before-renderer", 1250.0);
}
