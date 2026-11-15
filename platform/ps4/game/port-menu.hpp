#pragma once
#include <imgui.h>
#include <algorithm>

// Scoped to port menus by the caller. No global style/font changes: startup,
// storage recovery, shader preparation and shutdown keep their existing UI.
namespace port_menu {
class Panel {
    bool contentOpen_ = true;
public:
    Panel(const char* title, bool largeText) {
        const auto display = ImGui::GetIO().DisplaySize;
        ImGui::GetBackgroundDrawList()->AddRectFilled(ImVec2(0, 0), display, IM_COL32(7, 22, 48, 255));
        ImGui::PushStyleColor(ImGuiCol_WindowBg, ImVec4(.055f, .075f, .11f, 1.f));
        ImGui::PushStyleColor(ImGuiCol_ChildBg, ImVec4(0, 0, 0, 0));
        ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(.94f, .96f, 1.f, 1.f));
        ImGui::PushStyleColor(ImGuiCol_Separator, ImVec4(.22f, .30f, .42f, 1.f));
        ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(28, 24));
        ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, 12.f);
        ImGui::PushStyleVar(ImGuiStyleVar_ItemSpacing, ImVec2(12, 10));
        ImGui::SetNextWindowPos(ImVec2(display.x * .5f, display.y * .5f), ImGuiCond_Always, ImVec2(.5f, .5f));
        ImGui::SetNextWindowSize(ImVec2(std::min(1000.f, display.x * .88f), std::min(820.f, display.y * .9f)));
        ImGui::Begin("PSWaker port menu", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
            ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoNavInputs | ImGuiWindowFlags_NoNavFocus);
        ImGui::SetWindowFontScale(largeText ? 1.7f : 1.3f);
        ImGui::TextColored(ImVec4(.55f, .70f, .90f, 1.f), "PSWAKER");
        ImGui::TextWrapped("%s", title);
        ImGui::Separator();
        // Keep controller hints and release feedback outside the scrolling body.
        const float footer = 5 * ImGui::GetTextLineHeightWithSpacing() + ImGui::GetStyle().ItemSpacing.y;
        ImGui::PushID(title);
        ImGui::BeginChild("Content", ImVec2(0, -footer), ImGuiChildFlags_None,
            ImGuiWindowFlags_NoNavInputs | ImGuiWindowFlags_NoNavFocus);
    }
    void footer() {
        ImGui::EndChild();
        ImGui::PopID();
        contentOpen_ = false;
        ImGui::Separator();
    }
    ~Panel() {
        if (contentOpen_) { ImGui::EndChild(); ImGui::PopID(); }
        ImGui::End();
        ImGui::PopStyleVar(3);
        ImGui::PopStyleColor(4);
    }
    Panel(const Panel&) = delete;
    Panel& operator=(const Panel&) = delete;
};

inline void row(const char* label, bool selected) {
    const auto origin = ImGui::GetCursorScreenPos();
    const float width = ImGui::GetContentRegionAvail().x;
    const float padding = ImGui::GetTextLineHeight() * .45f;
    const float wrap = std::max(1.f, width - padding * 2);
    const float height = ImGui::CalcTextSize(label, nullptr, false, wrap).y + padding * 2;
    ImGui::Dummy(ImVec2(width, height));
    auto* draw = ImGui::GetWindowDrawList();
    if (selected) {
        draw->AddRectFilled(origin, ImVec2(origin.x + width, origin.y + height), IM_COL32(24, 89, 190, 255), 6);
        ImGui::SetScrollHereY(.5f);
    }
    draw->AddText(ImGui::GetFont(), ImGui::GetFontSize(), ImVec2(origin.x + padding, origin.y + padding),
        ImGui::GetColorU32(ImGuiCol_Text), label, nullptr, wrap);
}
} // namespace port_menu
