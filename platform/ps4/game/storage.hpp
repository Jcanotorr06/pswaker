#pragma once
#include "controls-config.hpp"
#include <string>
#include <utility>

// Flush the closed temporary file, replace within its directory, then sync the
// directory. A failure after rename is an uncertain completion, never success.
extern "C" bool pswaker_commit_file(const char* temporary, const char* destination);

// Whole in-game save boundary: individual CARD writes target a staging GCI.
class SaveFile {
public:
    explicit SaveFile(std::string path) : path_(std::move(path)) {}
    bool check();
    bool canRestore() const;
    bool restore(); // Only called after the player explicitly selects Restore.
    bool begin();
    bool finish(bool completed);
    std::string testMode() const;
    const char* error() const { return error_.c_str(); }
    static const char* cardPath(const char* path);
    static bool rejectCardWrite(const char* path);
private:
    enum class Problem { None, Unavailable, InvalidTest, Recovery };
    bool failure(const char* reason, Problem problem = Problem::Unavailable);
    std::string path_, error_, testMode_;
    Problem problem_ = Problem::None;
    static thread_local SaveFile* active_;
};
extern "C" const char* pswaker_gci_path(const char* path);
extern "C" bool pswaker_save_begin(int slot);
extern "C" bool pswaker_save_check(int slot);
extern "C" bool pswaker_save_finish(bool completed);

class PortSettings {
public:
    explicit PortSettings(std::string root = "/data/pswaker") : root_(std::move(root)) {}
    bool check(); // Create/probe the shared profile and load text size and complete controls.
    bool largeText() const { return largeText_; }
    const ControlsConfig& controls() const { return controls_.config; }
    const char* controlsFeedback() const { return controls_.feedback; }
    bool setLargeText(bool large);
    // Save the whole controls section in one checked profile replacement.
    // False includes uncertain completion: no in-memory settings are changed.
    bool setControls(const ControlsConfig& config);
    const char* error() const { return error_.c_str(); }

private:
    bool read(std::string& contents, bool& large);
    bool failure(const std::string& path);
    std::string root_, error_;
    bool largeText_ = true;
    ControlsLoad controls_;
};
