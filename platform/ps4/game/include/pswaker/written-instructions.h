#pragma once
#include <cstddef>

// Game-thread only. Bounded DAT1 input, including its control tags and terminator.
// Reviewed USA message IDs become stable semantic tags; other messages stay native.
// Returned converted strings live through shutdown, including during an open dialog.
const char* pswaker_written_message(const char* source, size_t available, unsigned message);

// A retained J2D string contains ESC PS[action], never an expanded binding name.
// The display table is rebuilt at the shared applied-generation resume boundary.
const char* pswaker_written_name(unsigned action);

// One atomic inline slot, shared by BMG measurement/output and J2D rendering.
inline constexpr unsigned pswakerWrittenTag = 0x7e;
inline constexpr float pswakerWrittenCells = 4.5f;
