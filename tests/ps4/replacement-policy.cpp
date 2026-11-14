#include "replacement-policy.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <climits>

int main() {
    using namespace pswaker::replacement;
    // The caller enumerates matching keys, including source wildcards. No
    // texture bytes, key hashes, GPU handles or registration order assumptions.
    for (auto promptFamily : {KeyFamily::Pointer, KeyFamily::Source,
                              KeyFamily::PaletteWildcard, KeyFamily::TextureWildcard}) {
        for (auto packFamily : {KeyFamily::Pointer, KeyFamily::Source,
                                KeyFamily::PaletteWildcard, KeyFamily::TextureWildcard}) {
            std::array candidates{
                Candidate{11, packFamily, packMaximumPriority, 99},
                Candidate{22, promptFamily, promptPriority, 1}};
            assert(select(candidates) == 22);
            std::reverse(candidates.begin(), candidates.end());
            assert(select(candidates) == 22);
            candidates[0].sequence = 100;
            candidates[1].sequence = 1;
            assert(select(candidates) == 22);
        }
    }
    assert(select({}) == 0);
    const std::array sameKey{Candidate{1, KeyFamily::Pointer, 5, 1},
                             Candidate{2, KeyFamily::Pointer, 5, 2}};
    assert(select(sameKey) == 2);
    const std::array legacy{Candidate{1, KeyFamily::Pointer, -1, 1},
                            Candidate{2, KeyFamily::Source, packMaximumPriority, 2}};
    assert(select(legacy) == 1); // Ordinary replacement precedence stays pointer-first.
}
