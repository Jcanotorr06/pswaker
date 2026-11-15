#pragma once
#include "controls-config.hpp"
#include <dolphin/pad.h>
#include <array>

enum class PortScreen { Legend, Game, Settings, Quit, InputLost, Exit,
    Controls, Binding, DiscardControls, ApplyingControls, ControlsFailed, RestoreControls, Diagnostics };
enum class PortNavigation { None, Selection, GuidePage, Information };
struct PortScreenInfo {
    const char* title = nullptr; // A title opts this screen into the port-menu panel.
    const char* confirm = nullptr;
    const char* cancel = nullptr;
    PortNavigation navigation = PortNavigation::None;
};
// Shared by input and presentation so information scrolling and hints agree.
// Connection-dependent hints and release/status feedback stay contextual.
inline constexpr PortScreenInfo portScreenInfo(PortScreen screen) {
    switch (screen) {
    case PortScreen::Settings:
        return {"Port menu", "Confirm", "Resume game", PortNavigation::Selection};
    case PortScreen::Diagnostics:
        return {"Diagnostics", "Run action and resume", "Back to port menu", PortNavigation::Selection};
    case PortScreen::Legend:
        return {"Button guide", "Continue / Return to port menu", "Back (when opened from port menu)", PortNavigation::GuidePage};
    case PortScreen::Controls:
        return {"Controls", "Edit / Confirm selected action", "Back (asks before discarding edits)", PortNavigation::Selection};
    case PortScreen::Binding:
        return {"Choose a binding", "Assign pending binding", "Keep current pending binding", PortNavigation::Selection};
    case PortScreen::RestoreControls:
        return {"Restore default controls?", "Restore pending defaults", "Keep current pending edits", PortNavigation::Information};
    case PortScreen::DiscardControls:
        return {"Discard pending controls?", "Discard and return to port menu", "Keep editing", PortNavigation::Information};
    case PortScreen::ApplyingControls:
        return {"Applying controls..."};
    case PortScreen::ControlsFailed:
        return {"Controls could not be applied", "Retry Apply", "Discard and return to port menu", PortNavigation::Information};
    case PortScreen::InputLost:
        return {"Controller input lost", nullptr, nullptr, PortNavigation::Information};
    case PortScreen::Quit:
        return {"Quit PSWaker?", "Confirm quit", "Back to port menu", PortNavigation::Information};
    default:
        return {};
    }
}

enum class PortAction { Resume, ShowLegend, CheckFailedRead, ToggleText, Quit, SampleOutset, SampleForest, Transition, Gameplay, EditControls, ShowDiagnostics };
struct PortMenuItem { PortAction action; const char* label; };
inline constexpr std::array<PortMenuItem, 6> portMenuItems{{
    {PortAction::Resume, "Resume"},
    {PortAction::EditControls, "Controls"},
    {PortAction::ShowLegend, "Button guide"},
    {PortAction::ToggleText, "Text size"},
    {PortAction::ShowDiagnostics, "Diagnostics"},
    {PortAction::Quit, "Quit"},
}};
inline constexpr std::array<PortMenuItem, 5> portDiagnosticItems{{
    {PortAction::CheckFailedRead, "Check failed read in 5 seconds"},
    {PortAction::SampleOutset, "Measure Outset for two minutes"},
    {PortAction::SampleForest, "Measure forest for two minutes"},
    {PortAction::Transition, "Mark loading / transition start"},
    {PortAction::Gameplay, "Mark visible gameplay ready"},
}};
inline constexpr unsigned portGuidePages = 3;
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
    unsigned diagnosticsSelection = 0;
    unsigned guidePage = 0;
    // Signed D-pad scroll steps for information screens; presentation clamps at
    // its actual content bounds. Reset on screen entry, gated like selection.
    int informationScroll = 0;
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
