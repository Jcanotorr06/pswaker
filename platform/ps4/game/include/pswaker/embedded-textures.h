#pragma once

// Title proc owns the resource lifetime; source is the stock BTI pixel address.
void pswaker_title_texture_set(const void* owner, const void* source);
void pswaker_title_texture_released(const void* owner);
// Check before drawing the retained pane. False suppresses stock instructions;
// a failed registration is retried without changing the applied configuration.
bool pswaker_title_texture_ready(const void* owner);
void pswaker_title_missing_instruction(unsigned item, const char* reason);
