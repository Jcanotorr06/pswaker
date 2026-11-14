// Synthetic messages only. Public translation/display boundary, no game assets.
#include "written-instructions.hpp"
#include <cassert>
#include <cstring>
#include <string>
#include <vector>

unsigned defects = 0;
void pswaker_report_prompt_coverage(const char*, unsigned, const char* reason) {
    assert(reason && *reason);
    ++defects;
}

std::vector<char> convert(unsigned id, const std::vector<char>& input) {
    const char* output = pswaker_written_message(input.data(), input.size(), id);
    // Converted BMG contains NUL inside tags, so scan by tag lengths.
    std::vector<char> result;
    for (size_t pos = 0; output[pos];) {
        const size_t count = output[pos] == 0x1a ? static_cast<unsigned char>(output[pos + 1]) : 1;
        result.insert(result.end(), output + pos, output + pos + count);
        pos += count;
    }
    result.push_back(0);
    return result;
}
std::vector<char> bytes(const char* text) { return {text, text + std::strlen(text) + 1}; }

int main() {
    // An ID reviewed for START alone must not accept another control token.
    assert(convert(1108, bytes("Hold START/PAUSE then move.")) ==
           bytes("Control instruction unavailable.\nSee the port controls legend."));
    assert(defects == 1);

    // Preserve prose, hold/press, alternatives, colours, directional pictures
    // and trigger tags byte for byte. Only the reviewed name becomes semantic.
    const std::vector<char> prefix{'H','o','l','d',' ',0x1a,6,char(0xff),0,0,1};
    const std::vector<char> suffix{0x1a,6,char(0xff),0,0,0,' ', 'o','r',' ',
        0x1a,5,0,0,0x0a,';',' ',0x1a,5,0,0,0x18,' ',0x1a,5,0,0,0x0e,0};
    for (unsigned id : {816, 817, 1108, 3008}) {
        auto input = prefix;
        const auto literal = bytes(id == 1108 ? "START" : "START/PAUSE");
        input.insert(input.end(), literal.begin(), literal.end() - 1);
        input.insert(input.end(), suffix.begin(), suffix.end());
        auto expected = prefix;
        const char tag[]{0x1a,6,0,0,0x7e,5};
        expected.insert(expected.end(), std::begin(tag), std::end(tag));
        expected.insert(expected.end(), suffix.begin(), suffix.end());
        assert(convert(id, input) == expected);
        const char* retained = pswaker_written_message(input.data(), input.size(), id);
        assert(pswaker_written_message(input.data(), input.size(), id) == retained);
        assert(pswaker_register_prompt_adapter(nullptr, pswaker_refresh_written_instructions) == (id == 816));
        const AppliedControls defaults{ControlsConfig::defaults(), 10};
        assert(pswaker_refresh_prompts(defaults));
        assert(std::string(pswaker_written_name(5)) == "Options");
        auto applied = defaults;
        assert(applied.config.assign(GameAction::Start, ControlTarget::R3));
        applied.generation++;
        assert(pswaker_refresh_prompts(applied));
        assert(std::string(pswaker_written_name(5)) == "R3");
        assert(convert(id, input) == expected); // Same parsed bytes; name refreshed at draw.
        assert(pswaker_written_message(input.data(), input.size(), id) == retained);
    }

    const auto unrelated = bytes("A Button is a prop; START is an event name.");
    assert(pswaker_written_message(unrelated.data(), unrelated.size(), 500) == unrelated.data());
    const auto wrongSpan = bytes("RESTART the synthetic exhibit.");
    assert(convert(816, wrongSpan) == bytes("Control instruction unavailable.\nSee the port controls legend."));
    const auto duplicate = bytes("START/PAUSE or START/PAUSE");
    assert(convert(817, duplicate) == bytes("Control instruction unavailable.\nSee the port controls legend."));
    const std::vector<char> truncated{'S','T','A','R','T','/','P','A','U','S','E',0x1a,6};
    assert(convert(3008, truncated) == bytes("Control instruction unavailable.\nSee the port controls legend."));
    const std::vector<char> tagPayload{0x1a,16,0,0,'S','T','A','R','T','/','P','A','U','S','E',0,0};
    assert(convert(3008, tagPayload) == bytes("Control instruction unavailable.\nSee the port controls legend."));
    const auto newResource = bytes("Synthetic updated START caption");
    assert(convert(1108, newResource) == bytes("Control instruction unavailable.\nSee the port controls legend."));

    // These IDs describe system operations, not gameplay A or Start. Never guess.
    for (unsigned id : {18, 23, 37, 49, 54, 60, 96, 134, 612}) {
        const auto before = defects;
        assert(convert(id, unrelated) == bytes("This system instruction is unavailable\non PS4."));
        assert(defects == before + 1);
        convert(id, unrelated);
        assert(defects == before + 1);
    }

    const char* targets[]{"Cross", "Circle", "Square", "Triangle", "L1", "R1", "L3", "R3", "Options"};
    uint64_t generation = 50;
    for (auto action : gameActions) for (unsigned target = 0; target < 9; ++target) {
        AppliedControls applied{ControlsConfig::defaults(), generation++};
        assert(applied.config.assign(action, static_cast<ControlTarget>(target)));
        assert(pswaker_refresh_prompts(applied));
        assert(std::string(pswaker_written_name(static_cast<unsigned>(action))) == targets[target]);
    }
    auto invalid = AppliedControls{ControlsConfig::defaults(), generation++};
    invalid.config.bindings[0] = static_cast<ControlTarget>(99);
    const auto before = defects;
    assert(pswaker_refresh_prompts(invalid));
    assert(defects > before && std::string(pswaker_written_name(5)) == "?");
    assert(std::string(pswaker_written_name(99)) == "?");
}
