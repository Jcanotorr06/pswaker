#pragma once
#include "controls-config.hpp"
#include <dolphin/pad.h>
#include <array>

struct AppliedControls {
    ControlsConfig config;
    uint64_t generation = 0;
    // Descriptions of controls that cannot be remapped. Port controls are separate.
    static constexpr std::array<const char*, 3> fixedGameplay{
        "Left stick = Control Stick; Right stick = C Stick; D-pad = D-pad",
        "L2 / R2 = analog L / R; full press starts at 90% travel.",
        "L3 / R3 assignments are digital only; stick movement stays fixed."};
    static constexpr std::array<const char*, 2> fixedPort{
        "Touchpad click = Port settings; D-pad = Navigate",
        "Cross = Confirm; Circle = Cancel / Back"};
    std::array<std::string, 8> legend() const;
};
// Returns an independent read-only view of one whole generation, safe across publication.
AppliedControls pswaker_applied_controls();
// Startup calls this after a successful profile check. Apply MUST validate,
// persist successfully, then publish. Every successful publication (even identical
// values) increments generation once; rejection leaves snapshot/generation intact.
// Generation 0 is the initial default; overflow is rejected, never wrapped.
bool pswaker_publish_controls(const ControlsConfig& config);

enum class PortScreen { Legend, Game, Settings, Quit, InputLost, Exit,
    Controls, Binding, DiscardControls, ApplyingControls, ControlsFailed, RestoreControls };
enum class PortAction { Resume, ShowLegend, CheckFailedRead, ToggleText, Quit, SampleOutset, SampleForest, Transition, Gameplay, EditControls };
struct PortMenuItem { PortAction action; const char* label; };
inline constexpr std::array<PortMenuItem, 10> portMenuItems{{
    {PortAction::Resume, "Resume game"},
    {PortAction::ShowLegend, "DualShock 4 legend"},
    {PortAction::CheckFailedRead, "Resume and check failed read in 5 seconds"},
    {PortAction::ToggleText, "Change port text size"},
    {PortAction::Quit, "Quit game..."},
    {PortAction::SampleOutset, "Measure Outset (resume for two minutes)"},
    {PortAction::SampleForest, "Measure forest (resume for two minutes)"},
    {PortAction::Transition, "Mark loading / transition start and resume"},
    {PortAction::Gameplay, "Mark visible gameplay ready and resume"},
    {PortAction::EditControls, "Controls..."},
}};
struct PortView {
    PortScreen screen;
    unsigned selection;
    bool connected;
    bool releasing;
    ControlsConfig pendingControls{};
    unsigned controlsSelection = 0; // Six action rows, Restore defaults, Apply, Back.
    unsigned bindingSelection = 0;
    bool controlsDirty = false;
    std::string controlsError{};
};

// Called by the SDL input hook, including while the port UI is on screen.
void pswaker_poll_controls();
// First game frame, after installation/storage preparation screens have finished.
class PortSettings;
void pswaker_enable_controls(PortSettings& settings);
PortView pswaker_port_view();
void pswaker_log_controls();
void pswaker_toggle_text_size();
// PS4 PADRead uses the same authoritative sample and pause gate as the port UI.
extern "C" u32 pswaker_read_gamepad(PADStatus* status);
