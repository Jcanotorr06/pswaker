#pragma once
#include "prompts.hpp"
#include "pswaker/hud-pictures.h"

// Register at the shared before-resume boundary and seed after startup's applied
// publication. No pending configuration is read by this adapter.
bool pswaker_refresh_hud_prompts(void*, const AppliedControls& applied);
