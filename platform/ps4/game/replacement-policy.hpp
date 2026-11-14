#pragma once
#include <cstdint>
#include <limits>
#include <span>

// Public rule for the future #80 loader and Aurora's matching-key arbitration.
// Only the project prompt layer may use promptPriority. Pack registrations must
// be <= packMaximumPriority. Prompt ownership wins BEFORE key specificity,
// priority and registration sequence. Evaluate before consulting winner caches;
// any registration/unregistration invalidates Aurora's retained GX bindings.
namespace pswaker::replacement {
inline constexpr int32_t promptPriority = std::numeric_limits<int32_t>::max();
inline constexpr int32_t packMaximumPriority = promptPriority - 1;
enum class KeyFamily { Pointer, Source, PaletteWildcard, TextureWildcard };
struct Candidate {
    uint64_t id;
    KeyFamily family;
    int32_t priority;
    uint64_t sequence;
};
constexpr bool preferred(const Candidate& a, const Candidate& b) {
    if ((a.priority == promptPriority) != (b.priority == promptPriority))
        return a.priority == promptPriority;
    if (a.family != b.family) return a.family < b.family;
    if (a.priority != b.priority) return a.priority > b.priority;
    return a.sequence > b.sequence;
}
inline uint64_t select(std::span<const Candidate> candidates) {
    const Candidate* winner = nullptr;
    for (const auto& candidate : candidates)
        if (candidate.id && (!winner || preferred(candidate, *winner))) winner = &candidate;
    return winner ? winner->id : 0;
}
}
