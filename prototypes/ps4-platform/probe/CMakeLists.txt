cmake_minimum_required(VERSION 3.25)
project(pswaker_platform_diagnostic LANGUAGES C CXX ASM)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(PLATFORM_ROOT "$ENV{PS4_PORT_ROOT}")
set(DOLPHINPS4 "$ENV{DOLPHINPS4}")
include(${DOLPHINPS4}/toolchain/ps4-love-style.cmake)
add_compile_definitions(PS4_DEV_TOOLS=0)
include(FetchContent)
set(TRACY_ENABLE OFF CACHE BOOL "No profiler in this bounded diagnostic" FORCE)
FetchContent_Declare(tracy
  URL https://github.com/wolfpld/tracy/archive/refs/tags/v0.14.1.zip
  URL_HASH SHA256=908f3a2917fa86a247abfcf85dcf04bad1db6986a4d40f94b70512f3e9e98d5b
  DOWNLOAD_EXTRACT_TIMESTAMP FALSE
  SOURCE_SUBDIR ps4-headers-only)
FetchContent_MakeAvailable(tracy)
add_library(ps4_tracy_headers INTERFACE)
target_include_directories(ps4_tracy_headers INTERFACE "${tracy_SOURCE_DIR}/public")
add_library(Tracy::TracyClient ALIAS ps4_tracy_headers)
add_library(TracyClient ALIAS ps4_tracy_headers)

# Consume our source-built monolithic archive, with headers from the same build.
# Nothing is downloaded as a precompiled PS4 library.
file(MAKE_DIRECTORY "${PLATFORM_ROOT}/build/dawn/gen/include")
add_library(webgpu_dawn STATIC IMPORTED GLOBAL)
set_target_properties(webgpu_dawn PROPERTIES
  IMPORTED_LOCATION "${PLATFORM_ROOT}/build/dawn/src/dawn/native/libwebgpu_dawn.a"
  INTERFACE_INCLUDE_DIRECTORIES "${PLATFORM_ROOT}/src/dawn/include;${PLATFORM_ROOT}/build/dawn/gen/include")
add_library(dawn::webgpu_dawn ALIAS webgpu_dawn)
add_library(dawn::dawncpp_headers INTERFACE IMPORTED GLOBAL)
set_target_properties(dawn::dawncpp_headers PROPERTIES
  INTERFACE_INCLUDE_DIRECTORIES "${PLATFORM_ROOT}/src/dawn/include;${PLATFORM_ROOT}/build/dawn/gen/include")
set(AURORA_DAWN_PROVIDER vendor CACHE STRING "Use existing source-built Dawn" FORCE)
set(AURORA_SDL3_PROVIDER system CACHE STRING "Use selected source-built SDL3" FORCE)
set(SDL3_DIR "${PLATFORM_ROOT}/build/sdl3" CACHE PATH "Selected SDL3" FORCE)
set(FETCHCONTENT_SOURCE_DIR_ABSEIL-CPP "${PLATFORM_ROOT}/src/abseil" CACHE PATH "Selected Abseil" FORCE)
set(AURORA_ENABLE_EXAMPLES OFF CACHE BOOL "" FORCE)
set(AURORA_ENABLE_TESTS OFF CACHE BOOL "" FORCE)
set(AURORA_ENABLE_DVD OFF CACHE BOOL "Disc-free" FORCE)
set(AURORA_ENABLE_CARD OFF CACHE BOOL "Synthetic files only" FORCE)
set(AURORA_ENABLE_THP OFF CACHE BOOL "No game media" FORCE)
set(AURORA_CACHE_USE_ZSTD OFF CACHE BOOL "Uncompressed diagnostic cache" FORCE)
set(DAWN_ENABLE_VULKAN ON CACHE BOOL "" FORCE)
set(DAWN_ENABLE_DESKTOP_GL OFF CACHE BOOL "" FORCE)
set(DAWN_ENABLE_OPENGLES OFF CACHE BOOL "" FORCE)
add_subdirectory("${PLATFORM_ROOT}/src/aurora" aurora)

add_executable(platform_diagnostic main.cpp ${PS4_RUNTIME_SOURCES}
  "${PLATFORM_ROOT}/src/native-platform/ps4/input.cpp"
  "${PLATFORM_ROOT}/src/native-platform/ps4/native/platform.c"
  "${PLATFORM_ROOT}/src/native-platform/ps4/native/realpath.c")
target_compile_options(platform_diagnostic PRIVATE -ftls-model=initial-exec)
if(NOT PSWAKER_BUILD_ID)
  set(PSWAKER_BUILD_ID unrecorded)
endif()
target_compile_definitions(platform_diagnostic PRIVATE PSWAKER_BUILD_ID="${PSWAKER_BUILD_ID}")
target_include_directories(platform_diagnostic PRIVATE "${PLATFORM_ROOT}/src/aurora/lib")
target_include_directories(platform_diagnostic PRIVATE "${PLATFORM_ROOT}/src/native-platform/ps4")
target_link_options(platform_diagnostic PRIVATE "LINKER:--wrap=realpath")
target_link_libraries(platform_diagnostic PRIVATE aurora::core aurora::gx aurora::main aurora::vi
  z SceSysmodule SceSystemService SceUserService SceVideoOut SceAudioOut ScePad SceNet pthread)
ps4_link_mesa(platform_diagnostic)
ps4_add_eboot(platform_diagnostic)
