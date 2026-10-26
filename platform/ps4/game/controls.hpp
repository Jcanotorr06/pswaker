#pragma once
#include <dolphin/pad.h>
#include <array>

enum class PortScreen { Legend, Game, Settings, Quit, InputLost, Exit };
enum class PortAction { Resume, ShowLegend, CheckFailedRead, Quit };
struct PortMenuItem { PortAction action; const char* label; };
inline constexpr std::array<PortMenuItem, 4> portMenuItems{{
    {PortAction::Resume, "Resume game"},
    {PortAction::ShowLegend, "DualShock 4 legend"},
    {PortAction::CheckFailedRead, "Resume and check failed read in 5 seconds"},
    {PortAction::Quit, "Quit game..."},
}};
struct PortView {
    PortScreen screen;
    unsigned selection;
    bool connected;
    bool releasing;
};

// Called by the SDL input hook, including while the port UI is on screen.
void pswaker_poll_controls();
// First game frame, after installation/storage preparation screens have finished.
void pswaker_enable_controls();
PortView pswaker_port_view();
void pswaker_log_controls();
// PS4 PADRead uses the same authoritative sample and pause gate as the port UI.
extern "C" u32 pswaker_read_gamepad(PADStatus* status);
