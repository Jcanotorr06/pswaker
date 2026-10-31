#pragma once
#include <cstdint>
#include <cstdio>

// The caller owns a read-only stream. Validation never opens or writes user data.
bool pswaker_validate_image(FILE* image, char* error, size_t error_size,
                            void (*progress)(uint64_t, uint64_t) = nullptr);
bool pswaker_hash_stream(FILE* input, uint64_t size, char sha1[41],
                         void (*progress)(uint64_t, uint64_t) = nullptr);

// A passed full check, recorded for one build, installed image and package manifest.
struct ImageRecord {
    const char* manifest; // Records the owner image and program hashes.
    const char* path;     // Losing this file only costs one more full check.
    const char* build;
    char identity[512] = ""; // For logs; empty when the manifest is unreadable.
};
enum class ImageCheck { Failed, MatchedRecord, FullRecorded, FullUnrecorded };

// Size and file type are checked on every launch. The whole image is hashed only
// when the record does not match; only a passed full check is recorded.
ImageCheck pswaker_check_installed_image(FILE* image, ImageRecord& record, char* error, size_t error_size,
                                         void (*progress)(uint64_t, uint64_t) = nullptr);
