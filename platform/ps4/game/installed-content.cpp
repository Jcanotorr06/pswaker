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
    const auto fail = [&](const char* reason) {
        snprintf(error, error_size, "Installation error: %s. Rebuild the complete package on the computer and reinstall; existing saves/settings are preserved.", reason);
        return false;
    };
    if (!image) return fail("/app0/game.iso is missing or unreadable");
    struct stat info{};
    if (fstat(fileno(image), &info) || !S_ISREG(info.st_mode) || uint64_t(info.st_size) != image_size)
        return fail("installed image has an invalid size or file type");
    char actual[41];
    if (!pswaker_hash_stream(image, image_size, actual, progress))
        return fail("installed image read failed; partial content cannot be used");
    bool accepted = false;
    for (const char* expected : image_sha1) accepted |= strcmp(actual, expected) == 0;
    if (!accepted) return fail("installed image checksum is invalid");
    return true;
}

#if defined(PSWAKER_HOST_CONTENT_CHECK)
int main(int argc, char** argv) {
    FILE* image = argc == 2 ? fopen(argv[1], "rb") : nullptr;
    char error[512] = "Installation error: read failed. Rebuild the complete package and reinstall.";
    bool valid = pswaker_validate_image(image, error, sizeof error);
    if (image && fclose(image)) valid = false;
    if (!valid) { fprintf(stderr, "%s\n", error); return 14; }
    puts("Installed image verified");
}
#endif
