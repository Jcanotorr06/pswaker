#pragma once
#include "controls-config.hpp"
#include <dolphin/pad.h>
#include <array>

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
    unsigned controlsSelection = 0; // Six actions, inversion X/Y, Restore defaults, Apply, Back.
    unsigned bindingSelection = 0;
    bool controlsDirty = false;
    std::string controlsError{};
    bool refreshingPrompts = false;
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
