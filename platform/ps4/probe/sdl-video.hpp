#pragma once
#include <SDL3/SDL.h>

// SDL supplies events and a sized placeholder; Dawn owns the direct-display surface.
// The pinned dummy backend deliberately refuses automatic selection.
inline bool configure_console_sdl_video() {
  return SDL_SetHintWithPriority(SDL_HINT_VIDEO_DRIVER, "dummy", SDL_HINT_OVERRIDE);
}
