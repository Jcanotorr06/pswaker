/* Throwaway startup breadcrumbs. No heap, stdio, TLS or C++ initialization. */
#include <orbis/libkernel.h>

/* Native FreeBSD open flags, not the musl-facing fcntl.h values:
 * https://github.com/freebsd/freebsd-src/blob/releng/9.0/sys/sys/fcntl.h */
enum { NATIVE_WRITE = 1, NATIVE_APPEND = 8, NATIVE_CREATE = 0x200 };

static unsigned length(const char* text) {
  unsigned n = 0;
  while (text[n]) ++n;
  return n;
}

static void hex(char* out, unsigned value) {
  const char digits[] = "0123456789abcdef";
  for (unsigned i = 0; i < 8; ++i) out[i] = digits[(value >> ((7-i)*4)) & 15];
}

static int append(const char* path, const char* stage) {
  int fd = sceKernelOpen(path, NATIVE_WRITE | NATIVE_APPEND | NATIVE_CREATE, 0666);
  if (fd < 0) return fd;
  const char prefix[] = "[DEBUG-pswaker-startup] ";
  const char newline[] = "\n";
  int result = 0;
  const char* parts[] = {prefix, stage, newline};
  for (unsigned i = 0; i < 3; ++i) {
    const char* text = parts[i];
    unsigned remaining = length(text);
    while (remaining) {
      size_t written = sceKernelWrite(fd, text, remaining);
      if (!written || written > remaining) { result = -1; break; }
      text += written; remaining -= written;
    }
    if (result) break;
  }
  int sync = sceKernelFsync(fd);
  int close = sceKernelClose(fd);
  return result ? result : sync ? sync : close;
}

void pswaker_startup_stage(const char* stage) {
  sceKernelDebugOutText(0, "[DEBUG-pswaker-startup] ");
  sceKernelDebugOutText(0, stage);
  sceKernelDebugOutText(0, "\n");
  int directory = sceKernelMkdir("/data/pswaker-startup-probe", 0777);
  int primary = append("/data/pswaker-startup-probe/entry.log", stage);
  /* Independent fallback also records the native operation return values. */
  char status[] = "mkdir=0x00000000 primary-write=0x00000000";
  hex(status + 8, (unsigned)directory);
  hex(status + 33, (unsigned)primary);
  append("/data/pswaker-startup-probe.log", stage);
  append("/data/pswaker-startup-probe.log", status);
}

void pswaker_startup_entry(void) {
  pswaker_startup_stage("ENTRY before __libc_start_main; build=" PSWAKER_STARTUP_ID);
}

__attribute__((constructor(102))) static void after_crashlog_constructor(void) {
  pswaker_startup_stage("CONSTRUCTOR priority=102 reached");
}
