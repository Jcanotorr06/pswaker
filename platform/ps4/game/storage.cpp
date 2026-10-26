#include "storage.hpp"
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

extern "C" bool pswaker_commit_file(const char* temporary, const char* destination) {
    const int file = open(temporary, O_RDWR);
    if (file < 0) return false;
    const bool synced = fsync(file) == 0;
    const int syncError = errno;
    const bool closed = close(file) == 0;
    if (!synced) errno = syncError;
    if (!synced || !closed) return false;
    const std::string path(destination);
    const auto slash = path.find_last_of('/');
    const std::string parent = slash == std::string::npos ? "." : path.substr(0, slash);
    const int directory = open(parent.empty() ? "/" : parent.c_str(), O_RDONLY);
    if (directory < 0) return false;
    // Check directory sync support before replacing any previous valid file.
    bool good = fsync(directory) == 0;
    if (good) good = rename(temporary, destination) == 0;
    if (good) good = fsync(directory) == 0;
    const int error = errno;
    const bool directoryClosed = close(directory) == 0;
    if (!good) errno = error;
    return good && directoryClosed;
}

namespace {
bool replace(const std::string& path, const std::string& contents) {
    std::string temporary = path + ".tmp-XXXXXX";
    const int fd = mkstemp(temporary.data());
    if (fd < 0) return false;
    size_t done = 0;
    while (done < contents.size()) {
        const auto count = write(fd, contents.data() + done, contents.size() - done);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) break;
        done += count;
    }
    const int writeError = errno;
    const bool closed = close(fd) == 0;
    bool good = done == contents.size() && closed;
    if (done != contents.size()) errno = writeError ? writeError : EIO;
    if (good) good = pswaker_commit_file(temporary.c_str(), path.c_str());
    const int error = errno;
    unlink(temporary.c_str());
    errno = error;
    return good;
}
std::string trim(const std::string& line) {
    const auto first = line.find_first_not_of(" \t\r\n");
    return first == std::string::npos ? "" : line.substr(first, line.find_last_not_of(" \t\r\n") - first + 1);
}
constexpr const char* key = "PSWAKER_LARGE_TEXT=";
}

bool PortSettings::failure(const std::string& path) {
    error_ = path + ": " + strerror(errno ? errno : EIO);
    return false;
}
bool PortSettings::read(std::string& contents, bool& large) {
    const auto path = root_ + "/settings.ini";
    FILE* file = fopen(path.c_str(), "rb");
    if (!file) return errno == ENOENT ? true : failure(path);
    char buffer[4096];
    while (const auto count = fread(buffer, 1, sizeof buffer, file)) {
        contents.append(buffer, count);
        if (contents.size() > 1024 * 1024) { fclose(file); errno = EFBIG; return failure(path); }
    }
    const bool good = !ferror(file);
    const bool closed = fclose(file) == 0;
    if (!good || !closed) return failure(path);
    size_t offset = 0;
    while (offset < contents.size()) {
        const auto end = contents.find('\n', offset);
        const auto line = trim(contents.substr(offset, end - offset));
        if (line == "[dev]") break; // Never apply developer overrides on PS4.
        if (line.starts_with(key)) {
            const auto value = trim(line.substr(strlen(key)));
            if (value != "0" && value != "1") { errno = EINVAL; return failure(path); }
            large = value == "1";
        }
        if (end == std::string::npos) break;
        offset = end + 1;
    }
    return true;
}
bool PortSettings::check() {
    error_.clear();
    for (const char* suffix : {"", "/saves", "/saves/USA", "/saves/USA/Card A", "/saves/USA/Card B"}) {
        const auto directory = root_ + suffix;
        if (mkdir(directory.c_str(), 0755) && errno != EEXIST) return failure(directory);
        std::string probe = directory + "/.write-check-XXXXXX";
        const int fd = mkstemp(probe.data());
        if (fd < 0) return failure(directory);
        if (close(fd)) { unlink(probe.c_str()); return failure(directory); }
        const bool good = replace(probe, "PSWaker storage check\n");
        const int error = errno;
        const bool removed = unlink(probe.c_str()) == 0;
        if (!good) errno = error;
        if (!good || !removed) return failure(directory);
    }
    std::string contents;
    bool large = true;
    if (!read(contents, large)) return false;
    largeText_ = large;
    return true;
}
bool PortSettings::setLargeText(bool large) {
    error_.clear();
    std::string contents, updated;
    bool previous = true;
    if (!read(contents, previous)) return false;
    size_t offset = 0;
    const std::string setting = std::string(key) + (large ? "1\n" : "0\n");
    bool inserted = false;
    while (offset < contents.size()) {
        const auto end = contents.find('\n', offset);
        const auto count = end == std::string::npos ? contents.size() - offset : end + 1 - offset;
        const auto raw = contents.substr(offset, count);
        const auto line = trim(raw);
        if (line == "[dev]") {
            updated += setting + contents.substr(offset);
            inserted = true;
            break;
        }
        if (!line.starts_with(key)) updated += raw;
        offset += count;
    }
    if (!inserted) {
        if (!updated.empty() && updated.back() != '\n') updated += '\n';
        updated += setting;
    }
    if (!replace(root_ + "/settings.ini", updated)) return failure(root_ + "/settings.ini");
    largeText_ = large;
    return true;
}
