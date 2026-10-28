#pragma once
#include <cstdint>
#include <cstdio>

// The caller owns a read-only stream. Validation never opens or writes user data.
bool pswaker_validate_image(FILE* image, char* error, size_t error_size,
                            void (*progress)(uint64_t, uint64_t) = nullptr);
bool pswaker_hash_stream(FILE* input, uint64_t size, char sha1[41],
                         void (*progress)(uint64_t, uint64_t) = nullptr);
