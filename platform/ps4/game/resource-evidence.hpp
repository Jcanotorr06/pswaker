#pragma once

// Records bytes for memory quantities and a count for buffers. Elapsed time uses
// the caller's launch clock; failed flexible-memory queries retain their status.
void pswaker_log_resources(const char* phase, double elapsedMs);
