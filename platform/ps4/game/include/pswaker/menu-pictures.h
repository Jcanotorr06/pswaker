#pragma once
#include <cstdint>

// Native game menus consume applied gameplay bindings. Port settings,
// confirmation and reconnect screens must never call this adapter.
enum class PswakerMenuControl : uint8_t { A, B, L, R };
enum class PswakerMenuFamily : uint8_t { FileSelect, SeaChart, Window };
enum class PswakerMenuInstruction : uint8_t { FileSelect, WindowClose };
using PswakerMenuApply = void (*)(void* picture, const void* texture);

void pswaker_menu_picture_set(void* picture, PswakerMenuFamily family,
                              PswakerMenuControl control, PswakerMenuApply apply);
void pswaker_menu_picture_released(void* picture);
// Accurate text for context-specific accepted alternatives, cached at the same
// refresh boundary as retained pictures. The caller controls visibility.
const char* pswaker_menu_instruction(PswakerMenuInstruction instruction);
void pswaker_menu_missing_picture(PswakerMenuFamily family, unsigned tag);
