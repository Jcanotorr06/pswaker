#pragma once
#include <string>
#include <utility>

// Flush the closed temporary file, replace within its directory, then sync the
// directory. A failure after rename is an uncertain completion, never success.
extern "C" bool pswaker_commit_file(const char* temporary, const char* destination);

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
