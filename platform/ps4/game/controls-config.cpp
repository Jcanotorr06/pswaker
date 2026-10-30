#include "controls-config.hpp"
#include <algorithm>

namespace {
constexpr std::array<const char*, 6> actionNames{"A", "B", "X", "Y", "Z", "Start"};
constexpr std::array<const char*, 9> targetNames{
    "Cross", "Circle", "Square", "Triangle", "L1", "R1", "L3", "R3", "Options"};
std::string_view trim(std::string_view text) {
    const auto first = text.find_first_not_of(" \t\r\n");
    return first == text.npos ? std::string_view{} : text.substr(first, text.find_last_not_of(" \t\r\n") - first + 1);
}
}

const char* control_action_name(GameAction action) { return actionNames.at(static_cast<unsigned>(action)); }
const char* control_target_name(ControlTarget target) { return targetNames.at(static_cast<unsigned>(target)); }
bool ControlsConfig::valid() const {
    std::array<bool, 9> used{};
    for (const auto target : bindings) {
        const auto index = static_cast<unsigned>(target);
        if (index >= used.size() || used[index]) return false;
        used[index] = true;
    }
    return true;
}
bool ControlsConfig::assign(GameAction action, ControlTarget target) {
    const auto index = static_cast<unsigned>(action);
    if (index >= bindings.size() || static_cast<unsigned>(target) >= targetNames.size() || !valid()) return false;
    const auto occupied = std::find(bindings.begin(), bindings.end(), target);
    if (occupied != bindings.end()) *occupied = bindings[index];
    bindings[index] = target;
    return true;
}

ControlsLoad parse_controls(std::string_view profile) {
    ControlsConfig config;
    std::array<bool, 9> seen{}; // version, six bindings, two inversion switches
    bool inControls = false, found = false;
    const auto invalid = [](const char* reason) { return ControlsLoad{ControlsConfig::defaults(), reason}; };
    while (!profile.empty()) {
        const auto end = profile.find('\n');
        const auto line = trim(profile.substr(0, end));
        profile = end == profile.npos ? std::string_view{} : profile.substr(end + 1);
        if (line.empty() || line.front() == '#' || line.front() == ';') continue;
        if (line.front() == '[') {
            if (line == "[controls]") {
                if (found) return invalid("Saved controls contain duplicate sections. Complete defaults are in use.");
                found = inControls = true;
            } else {
                // A damaged controls header must not masquerade as an absent section.
                if (line.starts_with("[controls")) return invalid("Saved controls section is malformed. Complete defaults are in use.");
                inControls = false;
            }
            continue;
        }
        if (!inControls) continue;
        const auto equals = line.find('=');
        if (equals == line.npos) return invalid("Saved controls are malformed. Complete defaults are in use.");
        const auto key = trim(line.substr(0, equals));
        const auto value = trim(line.substr(equals + 1));
        unsigned index = 0;
        if (key == "version") {
            if (value != "1") return invalid("Saved controls version is unsupported. Complete defaults are in use.");
        } else if (key == "invert_camera_x" || key == "invert_camera_y") {
            index = key == "invert_camera_x" ? 7 : 8;
            if (value != "0" && value != "1") return invalid("Saved camera inversion is invalid. Complete defaults are in use.");
            (index == 7 ? config.invertCameraX : config.invertCameraY) = value == "1";
        } else {
            const auto action = std::find(actionNames.begin(), actionNames.end(), key);
            const auto target = std::find(targetNames.begin(), targetNames.end(), value);
            if (action == actionNames.end() || target == targetNames.end())
                return invalid("Saved controls contain unsupported or reserved values. Complete defaults are in use.");
            index = 1 + (action - actionNames.begin());
            config.bindings[index - 1] = static_cast<ControlTarget>(target - targetNames.begin());
        }
        if (seen[index]) return invalid("Saved controls contain duplicate keys. Complete defaults are in use.");
        seen[index] = true;
    }
    if (!found) return {};
    if (std::find(seen.begin(), seen.end(), false) != seen.end())
        return invalid("Saved controls are incomplete. Complete defaults are in use.");
    if (!config.valid()) return invalid("Saved controls share a button between actions. Complete defaults are in use.");
    return {config, ""};
}

std::string serialize_controls(const ControlsConfig& config) {
    if (!config.valid()) return {};
    std::string section = "[controls]\nversion=1\n";
    for (const auto action : gameActions)
        section += std::string(control_action_name(action)) + "=" + control_target_name(config.binding(action)) + "\n";
    section += std::string("invert_camera_x=") + (config.invertCameraX ? "1\n" : "0\n");
    section += std::string("invert_camera_y=") + (config.invertCameraY ? "1\n" : "0\n");
    return section;
}
