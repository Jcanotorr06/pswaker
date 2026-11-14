#pragma once

// Title proc owns the resource lifetime; source is the stock BTI pixel address.
void pswaker_title_texture_set(const void* owner, const void* source);
void pswaker_title_texture_released(const void* owner);
