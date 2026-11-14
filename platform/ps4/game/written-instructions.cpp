#include "written-instructions.hpp"
#include <array>
#include <cstring>
#include <optional>
#include <string_view>
#include <vector>
#if defined(__ORBIS__)
#include <dolphin/types.h>
class JKRHeap;
#include "pc/game_hooks/jkr_heap.h"
#endif

void pswaker_report_prompt_coverage(const char*, unsigned, const char*);

namespace {
struct ReviewedMessage {
    unsigned id;
    std::string_view token;
    std::vector<char> converted;
    bool reported = false;
};
// Only identifiers and control-name tokens, never extracted instruction wording.
std::array<ReviewedMessage, 4> reviewed{{
    {816, "START/PAUSE", {}, false}, {817, "START/PAUSE", {}, false},
    {1108, "START", {}, false}, {3008, "START/PAUSE", {}, false}}};
constexpr std::array<unsigned, 9> unsupported{18, 23, 37, 49, 54, 60, 96, 134, 612};
std::array<bool, unsupported.size()> unsupportedReported{};
std::array<std::string, 6> names{};
std::optional<uint64_t> generation;
constexpr char unavailable[] = "This system instruction is unavailable\non PS4.";
constexpr char changed[] = "Control instruction unavailable.\nSee the port controls legend.";

bool word(unsigned char ch) {
    return (ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z') ||
           (ch >= '0' && ch <= '9') || ch == '_' || ch == '/';
}
void report(ReviewedMessage& entry, const char* reason) {
    if (!entry.reported) pswaker_report_prompt_coverage("written-message", entry.id, reason);
    entry.reported = true;
}
}

const char* pswaker_written_message(const char* source, size_t available, unsigned message) {
    // All allocations in game hooks use host memory, never the current game heap.
#if defined(__ORBIS__)
    JKRPcHostAllocScope host;
#endif
    if (!source) return source;
    for (size_t i = 0; i < unsupported.size(); ++i) {
        if (message != unsupported[i]) continue;
        if (!unsupportedReported[i]) pswaker_report_prompt_coverage("written-message", message,
            "System or peripheral instruction has no approved PS4 equivalent; suppressed");
        unsupportedReported[i] = true;
        return unavailable;
    }
    for (auto& entry : reviewed) {
        if (entry.id != message) continue;
        // Tags may contain NUL. Never use strlen on BMG content, or search its
        // tag payloads as text. Bound all reads by the DAT1 block supplied by game.
        std::vector<char> output;
        unsigned replacements = 0;
        bool terminated = false;
        for (size_t pos = 0; pos < available && pos < 65536;) {
            const unsigned char ch = source[pos];
            if (ch == 0) { terminated = true; break; }
            if (ch == 0x1a) {
                if (available - pos < 2) break;
                const size_t length = static_cast<unsigned char>(source[pos + 1]);
                if (length < 5 || length > available - pos) break;
                output.insert(output.end(), source + pos, source + pos + length);
                pos += length;
                continue;
            }
            const auto token = entry.token;
            if (token.size() <= available - pos &&
                std::memcmp(source + pos, token.data(), token.size()) == 0 &&
                (pos == 0 || !word(source[pos - 1])) &&
                (pos + token.size() == available || !word(source[pos + token.size()]))) {
                // Private BMG tag: an inline written action, not a button icon.
                constexpr char tag[]{0x1a, 6, 0, 0, pswakerWrittenTag,
                    static_cast<char>(GameAction::Start)};
                output.insert(output.end(), std::begin(tag), std::end(tag));
                ++replacements;
                pos += token.size();
            } else {
                output.push_back(source[pos++]);
            }
        }
        if (!terminated || replacements != 1) {
            report(entry, "Reviewed written control span missing, duplicated or malformed; suppressed");
            return changed;
        }
        output.push_back(0);
        if (entry.converted.empty()) entry.converted = std::move(output);
        else if (entry.converted != output) {
            // Never invalidate a pointer held by a parser or guess about a new resource.
            report(entry, "Reviewed message changed during its retained lifetime; suppressed");
            return changed;
        }
        return entry.converted.data();
    }
    return source;
}

bool pswaker_refresh_written_instructions(void*, const AppliedControls& applied) {
#if defined(__ORBIS__)
    JKRPcHostAllocScope host;
#endif
    if (generation == applied.generation) return true;
    std::array<std::string, 6> next;
    for (const auto action : gameActions) {
        const auto result = resolve_ps4_prompt({action, PromptContext::Gameplay}, applied);
        if (result.status == PromptStatus::Unresolved) {
            pswaker_report_prompt_coverage("written-binding", static_cast<unsigned>(action), result.reason.c_str());
            next[static_cast<unsigned>(action)] = "?";
        } else next[static_cast<unsigned>(action)] = result.name;
    }
    names = std::move(next);
    generation = applied.generation;
    return true;
}

const char* pswaker_written_name(unsigned action) {
    return action < names.size() && !names[action].empty() ? names[action].c_str() : "?";
}
