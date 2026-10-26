#pragma once
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
    bool failure(const char* reason);
    std::string path_, error_, testMode_;
    static thread_local SaveFile* active_;
};
extern "C" const char* pswaker_gci_path(const char* path);
extern "C" bool pswaker_save_begin(int slot);
extern "C" bool pswaker_save_check(int slot);
extern "C" bool pswaker_save_finish(bool completed);

class PortSettings {
public:
    explicit PortSettings(std::string root = "/data/pswaker") : root_(std::move(root)) {}
    bool check(); // Create/probe the shared profile and load its port setting.
    bool largeText() const { return largeText_; }
    bool setLargeText(bool large);
    const char* error() const { return error_.c_str(); }

private:
    bool read(std::string& contents, bool& large);
    bool failure(const std::string& path);
    std::string root_, error_;
    bool largeText_ = true;
};
