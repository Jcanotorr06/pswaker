#pragma once
#include <array>
#include <cstdint>
#include <string>
#include <string_view>

enum class GameAction { A, B, X, Y, Z, Start };
enum class ControlTarget { Cross, Circle, Square, Triangle, L1, R1, L3, R3, Options };
inline constexpr std::array<GameAction, 6> gameActions{
    GameAction::A, GameAction::B, GameAction::X, GameAction::Y, GameAction::Z, GameAction::Start};

// A complete value: no unbound actions and no shared targets.
struct ControlsConfig {
    std::array<ControlTarget, 6> bindings{ControlTarget::Cross, ControlTarget::Circle,
        ControlTarget::Square, ControlTarget::Triangle, ControlTarget::R1, ControlTarget::Options};
    bool invertCameraX = false;
    bool invertCameraY = false;
    static ControlsConfig defaults() { return {}; }
    bool valid() const;
    bool assign(GameAction action, ControlTarget target);
    ControlTarget binding(GameAction action) const { return bindings.at(static_cast<unsigned>(action)); }
    bool operator==(const ControlsConfig&) const = default;
};

struct ControlsLoad {
    ControlsConfig config;
    // Empty for a valid or absent section. Static text, never an I/O error.
    const char* feedback = "";
};
const char* control_action_name(GameAction action);
const char* control_target_name(ControlTarget target);
// Parse the whole profile. Invalid sections yield complete defaults, never partial values.
ControlsLoad parse_controls(std::string_view profile);
// A complete versioned section, or an empty string for an invalid value.
std::string serialize_controls(const ControlsConfig& config);

// One authoritative generation, shared by gameplay and presentation. Kept free
// of console/game headers so semantic prompts can also be checked on the host.
struct AppliedControls {
    ControlsConfig config;
    uint64_t generation = 0;
    std::array<std::string, 8> legend() const;
    std::array<std::string, 3> fixedGameplay() const;
    std::array<std::string, 2> fixedPort() const;
};
AppliedControls pswaker_applied_controls();
// Startup publishes after the profile check; Apply validates and saves first.
// Each successful publication increments once, including identical values.
// Invalid values and generation overflow are rejected without publication.
bool pswaker_publish_controls(const ControlsConfig& config);
