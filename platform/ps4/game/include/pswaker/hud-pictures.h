#pragma once
#include <cstdint>

// Meter presentation only. These name game controls, never physical bindings.
enum class PswakerHudControl : uint8_t { A, B, X, Y, Z, Start, L, R, DPad };
using PswakerHudApply = void (*)(void* picture, const void* texture);

// The game owns pictures; the adapter retains them until release. A description
// keeps its native action/weapon texture alongside the resolved control. Its
// buffer remains game-owned and may be rewritten by the next context change.
void pswaker_hud_picture_set(void* picture, PswakerHudControl control, PswakerHudApply apply);
void pswaker_hud_description_set(void* picture, PswakerHudControl control, uint16_t status,
                                const void* texture, PswakerHudApply apply);
void pswaker_hud_picture_released(void* picture);
