// This checkpoint deliberately has no texture-pack loader.
#include "pc/pc_hd_textures.h"
extern "C" {
void pc_hd_textures_init(const char*) {}
void pc_hd_textures_frame_end(unsigned int) {}
bool cos_hd_textures_set_enabled(bool) { return false; }
bool cos_hd_textures_enabled() { return false; }
void pc_hd_textures_set_stats_every(unsigned int) {}
}
