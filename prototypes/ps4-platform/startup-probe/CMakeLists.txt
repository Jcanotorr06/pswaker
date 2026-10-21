cmake_minimum_required(VERSION 3.25)
project(pswaker_startup_probe LANGUAGES C CXX ASM)
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include(${DOLPHINPS4}/toolchain/ps4-love-style.cmake)

# Instrument the selected entry code without replacing its process parameters,
# malloc replacement table or handoff to __libc_start_main.
file(READ ${DOLPHINPS4}/port/ps4_crt1.S crt)
set(original "_start:\n    jmp _start_ps4_c")
string(FIND "${crt}" "${original}" position)
if(position EQUAL -1)
  message(FATAL_ERROR "Unexpected selected CRT entry")
endif()
string(REPLACE "${original}" "_start:
    pushq %rdi
    pushq %rbx
    movq %rsp, %rbx
    andq $-16, %rsp
    call pswaker_startup_entry
    movq %rbx, %rsp
    popq %rbx
    popq %rdi
    jmp _start_ps4_c" crt "${crt}")
file(WRITE ${CMAKE_BINARY_DIR}/startup-crt1.S "${crt}")
execute_process(COMMAND ${CMAKE_C_COMPILER} -target x86_64-pc-freebsd12-elf -c
  ${CMAKE_BINARY_DIR}/startup-crt1.S -o ${PS4_CRT1} COMMAND_ERROR_IS_FATAL ANY)

# Preserve the runtime test itself; isolate its scratch files from the full probe.
file(READ ${CMAKE_CURRENT_LIST_DIR}/../runtime-preflight/main.cpp body)
string(REPLACE "/data/pswaker-diagnostic-prototype" "/data/pswaker-startup-probe" body "${body}")
file(WRITE ${CMAKE_BINARY_DIR}/runtime-body.cpp "${body}")
add_executable(startup_probe main.cpp early.c ${PS4_RUNTIME_SOURCES})
target_include_directories(startup_probe PRIVATE ${CMAKE_BINARY_DIR})
target_compile_definitions(startup_probe PRIVATE PSWAKER_STARTUP_ID="${PSWAKER_STARTUP_ID}")
target_compile_options(startup_probe PRIVATE -ftls-model=initial-exec)
set_source_files_properties(early.c PROPERTIES COMPILE_OPTIONS "-fno-builtin;-fno-stack-protector;-mgeneral-regs-only")
target_link_libraries(startup_probe PRIVATE SceSysmodule SceSystemService SceVideoOut SceUserService pthread)
ps4_add_eboot(startup_probe)
