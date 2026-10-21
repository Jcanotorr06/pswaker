// Throwaway host reproduction of the SDL startup boundary; no PS4/GPU execution.
#include <SDL3/SDL.h>
#include <cstdio>
#include <cstring>
#include "../probe/sdl-video.hpp"

int main(int argc, char** argv) {
  SDL_ResetHint(SDL_HINT_VIDEO_DRIVER);
  for (int i = 0; i < SDL_GetNumVideoDrivers(); ++i)
    std::printf("compiled-video-driver=%s\n", SDL_GetVideoDriver(i));
  if (argc == 2 && std::strcmp(argv[1], "--candidate") == 0 && !configure_console_sdl_video()) {
    std::printf("FAIL SDL driver configuration: %s\n",SDL_GetError());
    return 22;
  }
  if (!SDL_InitSubSystem(SDL_INIT_EVENTS | SDL_INIT_VIDEO)) {
    std::printf("FAIL SDL startup: %s\n", SDL_GetError());
    return 20;
  }
  const auto props = SDL_CreateProperties();
  SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_WIDTH_NUMBER, 1920);
  SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_HEIGHT_NUMBER, 1080);
  SDL_SetNumberProperty(props, SDL_PROP_WINDOW_CREATE_FLAGS_NUMBER,
    SDL_WINDOW_HIGH_PIXEL_DENSITY | SDL_WINDOW_HIDDEN | SDL_WINDOW_RESIZABLE);
  SDL_SetBooleanProperty(props, SDL_PROP_WINDOW_CREATE_EXTERNAL_GRAPHICS_CONTEXT_BOOLEAN, true);
  auto* window = SDL_CreateWindowWithProperties(props);
  int width = 0, height = 0;
  if (!window || !SDL_GetWindowSizeInPixels(window, &width, &height) || width != 1920 || height != 1080) {
    std::printf("FAIL SDL external-context placeholder window: %s\n", SDL_GetError());
    return 21;
  }
  std::printf("PASS SDL startup driver=%s window=%dx%d external-context=true\n",
    SDL_GetCurrentVideoDriver(), width, height);
  SDL_DestroyWindow(window);
  SDL_DestroyProperties(props);
  SDL_Quit();
}
