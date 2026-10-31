#include "installed-content.hpp"
#include <image-contract.hpp>
#include <algorithm>
#include <array>
#include <cstring>
#include <sys/stat.h>
#include <unistd.h>

namespace {
// SHA-1, FIPS 180-1. Adapted from the pinned SwitchWaker pc_assets.cpp validator
// (GPL-3.0); the same digest is used by the host content contract.
struct Sha1 {
    uint32_t h[5] = {0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0};
    uint8_t buffer[64]{};
    uint64_t length = 0;
    static uint32_t rotate(uint32_t v, unsigned n) { return (v << n) | (v >> (32 - n)); }
    void block(const uint8_t* input) {
        uint32_t w[80];
        for (unsigned i = 0; i < 16; ++i)
            w[i] = uint32_t(input[i*4]) << 24 | uint32_t(input[i*4+1]) << 16 |
                   uint32_t(input[i*4+2]) << 8 | input[i*4+3];
        for (unsigned i = 16; i < 80; ++i) w[i] = rotate(w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16], 1);
        uint32_t a=h[0], b=h[1], c=h[2], d=h[3], e=h[4];
        for (unsigned i = 0; i < 80; ++i) {
            uint32_t f, k;
            if (i < 20) { f=(b&c)|(~b&d); k=0x5a827999; }
            else if (i < 40) { f=b^c^d; k=0x6ed9eba1; }
            else if (i < 60) { f=(b&c)|(b&d)|(c&d); k=0x8f1bbcdc; }
            else { f=b^c^d; k=0xca62c1d6; }
            const uint32_t t=rotate(a,5)+f+e+k+w[i];
            e=d; d=c; c=rotate(b,30); b=a; a=t;
        }
        h[0]+=a; h[1]+=b; h[2]+=c; h[3]+=d; h[4]+=e;
    }
    void update(const uint8_t* input, size_t size) {
        size_t used = length % 64;
        length += size;
        while (size) {
            const size_t take = std::min(size, 64-used);
            memcpy(buffer+used, input, take);
            used+=take; input+=take; size-=take;
            if (used == 64) { block(buffer); used=0; }
        }
    }
    void finish(char out[41]) {
        const uint64_t bits=length*8;
        const uint8_t marker=0x80, zero=0;
        update(&marker,1);
        while (length%64 != 56) update(&zero,1);
        uint8_t tail[8];
        for (unsigned i=0; i<8; ++i) tail[i]=uint8_t(bits>>(56-i*8));
        update(tail,8);
        for (unsigned i=0; i<5; ++i) snprintf(out+i*8,9,"%08x",h[i]);
    }
};

bool failure(char* error, size_t error_size, const char* reason) {
    snprintf(error, error_size, "Installation error: %s. Rebuild the complete package on the computer and reinstall; existing saves/settings are preserved.", reason);
    return false;
}

bool shaped(FILE* image, struct stat& info, char* error, size_t error_size) {
    if (!image) return failure(error, error_size, "/app0/game.iso is missing or unreadable");
    if (fstat(fileno(image), &info) || !S_ISREG(info.st_mode) || uint64_t(info.st_size) != image_size)
        return failure(error, error_size, "installed image has an invalid size or file type");
    return true;
}

bool identify(const struct stat& image, ImageRecord& record) {
    FILE* manifest = fopen(record.manifest, "rb");
    struct stat info{};
    char sha1[41];
    bool good = manifest && !fstat(fileno(manifest), &info) && S_ISREG(info.st_mode) &&
                pswaker_hash_stream(manifest, info.st_size, sha1);
    if (manifest && fclose(manifest)) good = false;
    const int length = good ? snprintf(record.identity, sizeof record.identity,
        "pswaker-image-check-1 build=%s size=%llu mtime=%lld manifest-sha1=%s", record.build,
        (unsigned long long)image.st_size, (long long)image.st_mtime, sha1) : -1;
    if (length > 0 && size_t(length) < sizeof record.identity) return true;
    record.identity[0] = 0;
    return false;
}

bool recorded(const ImageRecord& record) {
    FILE* input = fopen(record.path, "rb");
    if (!input) return false;
    char contents[sizeof record.identity + 2];
    const size_t length = fread(contents, 1, sizeof contents, input);
    const bool closed = fclose(input) == 0;
    const size_t expected = strlen(record.identity);
    return closed && length == expected + 1 && !memcmp(contents, record.identity, expected) &&
           contents[expected] == '\n';
}

// A torn record cannot match, so it needs no backup or directory sync.
bool store(const ImageRecord& record) {
    FILE* output = fopen(record.path, "wb");
    if (!output) return false;
    bool good = fprintf(output, "%s\n", record.identity) > 0 && fflush(output) == 0 &&
                fsync(fileno(output)) == 0;
    if (fclose(output)) good = false;
    return good;
}
}

bool pswaker_hash_stream(FILE* input, uint64_t size, char sha1[41],
                         void (*progress)(uint64_t, uint64_t)) {
    if (!input || fseek(input, 0, SEEK_SET)) return false;
    Sha1 hash;
    std::array<uint8_t, 64*1024> buffer;
    uint64_t read = 0;
    if (progress) progress(0, size);
    while (read < size) {
        const size_t wanted = std::min(uint64_t(buffer.size()), size-read);
        if (fread(buffer.data(), 1, wanted, input) != wanted) return false;
        hash.update(buffer.data(), wanted);
        read += wanted;
        if (progress && read % (4*1024*1024) == 0) progress(read, size);
    }
    hash.finish(sha1);
    if (progress) progress(size, size);
    return true;
}

bool pswaker_validate_image(FILE* image, char* error, size_t error_size,
                            void (*progress)(uint64_t, uint64_t)) {
    struct stat info{};
    if (!shaped(image, info, error, error_size)) return false;
    char actual[41];
    if (!pswaker_hash_stream(image, image_size, actual, progress))
        return failure(error, error_size, "installed image read failed; partial content cannot be used");
    bool accepted = false;
    for (const char* expected : image_sha1) accepted |= strcmp(actual, expected) == 0;
    if (!accepted) return failure(error, error_size, "installed image checksum is invalid");
    return true;
}

ImageCheck pswaker_check_installed_image(FILE* image, ImageRecord& record, char* error, size_t error_size,
                                         void (*progress)(uint64_t, uint64_t)) {
    struct stat info{};
    if (!shaped(image, info, error, error_size)) return ImageCheck::Failed;
    const bool identified = identify(info, record);
    if (identified && recorded(record)) return ImageCheck::MatchedRecord;
    if (!pswaker_validate_image(image, error, error_size, progress)) return ImageCheck::Failed;
    return identified && store(record) ? ImageCheck::FullRecorded : ImageCheck::FullUnrecorded;
}

#if defined(PSWAKER_HOST_CONTENT_CHECK)
// content-check IMAGE [MANIFEST RECORD BUILD]
int main(int argc, char** argv) {
    FILE* image = argc == 2 || argc == 5 ? fopen(argv[1], "rb") : nullptr;
    char error[512] = "Installation error: read failed. Rebuild the complete package and reinstall.";
    auto check = ImageCheck::Failed;
    if (argc == 5) {
        ImageRecord record{argv[2], argv[3], argv[4]};
        check = pswaker_check_installed_image(image, record, error, sizeof error);
    } else if (pswaker_validate_image(image, error, sizeof error)) check = ImageCheck::FullUnrecorded;
    if (image && fclose(image)) check = ImageCheck::Failed;
    if (check == ImageCheck::Failed) { fprintf(stderr, "%s\n", error); return 14; }
    puts(argc == 2 ? "Installed image verified" :
         check == ImageCheck::MatchedRecord ? "Installed image verified by recorded full check" :
         check == ImageCheck::FullRecorded ? "Installed image verified; full check recorded" :
         "Installed image verified; full check not recorded");
}
#endif
