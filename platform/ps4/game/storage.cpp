#include "storage.hpp"
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <cstdint>
#include <memory>
#include <thread>
#include <chrono>

// Card callbacks run on a game worker, outside the port frame's host-allocation
// scope. Recovery strings/stages must not outlive an allocation in a game heap.
#if defined(PSWAKER_GAME_STORAGE)
extern void JKRPcBeginHostAlloc();
extern void JKRPcEndHostAlloc();
#endif
namespace {
struct StorageHostAlloc {
    StorageHostAlloc() {
#if defined(PSWAKER_GAME_STORAGE)
        JKRPcBeginHostAlloc();
#endif
    }
    ~StorageHostAlloc() {
#if defined(PSWAKER_GAME_STORAGE)
        JKRPcEndHostAlloc();
#endif
    }
};
}

extern "C" bool pswaker_commit_file(const char* temporary, const char* destination) {
    StorageHostAlloc hostAlloc;
    if (SaveFile::rejectCardWrite(destination)) { errno = ENOSPC; return false; }
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

// Distinguish a missing save from an unreadable save; never interpret an I/O
// error as permission to create a new profile. Limit reads to this USA GCI size.
bool readSave(const std::string& path, std::string& bytes, bool& exists) {
    FILE* file = fopen(path.c_str(), "rb");
    exists = file || errno != ENOENT;
    if (!file) return !exists;
    char buffer[4096];
    while (const auto count = fread(buffer, 1, sizeof buffer, file)) {
        bytes.append(buffer, count);
        if (bytes.size() > 0x18040) { fclose(file); errno = EFBIG; return false; }
    }
    const bool good = !ferror(file);
    const bool closed = fclose(file) == 0;
    return good && closed;
}
uint64_t bigEndian(const std::string& bytes, size_t offset, size_t count) {
    uint64_t value = 0;
    for (size_t i = 0; i < count; ++i) value = (value << 8) | uint8_t(bytes[offset+i]);
    return value;
}
bool validSave(const std::string& bytes) {
    if (bytes.size() != 0x18040 || bytes.compare(0, 6, "GZLE01") ||
        bytes.compare(8, 8, std::string("gczelda\0", 8)) || bigEndian(bytes, 0x38, 2) != 12 ||
        (uint8_t(bytes[7]) & 7) != 1 || bigEndian(bytes, 0x2c, 4) != 0 ||
        bigEndian(bytes, 0x30, 2) != 1 || bigEndian(bytes, 0x32, 2) != 3 ||
        bigEndian(bytes, 0x3c, 4) != 0x1c00)
        return false;
    // Both replicas must be complete. Do not invoke the game's automatic
    // replica repair on affected data or silently load reset slot contents.
    for (size_t block : {0x2040u, 0x4040u}) {
        uint16_t sum = 0, inverse = 0;
        for (size_t i = 0; i < 0x1ffc; i += 2) {
            const auto word = uint16_t(bigEndian(bytes, block+i, 2));
            sum += word; inverse += uint16_t(~word);
        }
        if (bigEndian(bytes, block+0x1ffc, 4) != ((uint32_t(sum) << 16) | inverse) ||
            bigEndian(bytes, block+4, 4) != 0) return false;
        for (size_t slot = 0; slot < 3; ++slot) {
            const size_t start = block + 8 + slot * 0x770;
            uint32_t total = 0, complement = 0;
            for (size_t i = 0; i < 0x768; ++i) {
                const uint8_t value = bytes[start+i];
                total += value; complement += ~uint32_t(value);
            }
            if (bigEndian(bytes, start+0x768, 8) != ((uint64_t(total) << 32) | complement)) return false;
        }
    }
    return bytes.compare(0x2040, 0x2000, bytes, 0x4040, 0x2000) == 0;
}
bool present(const std::string& path) {
    struct stat info{};
    return lstat(path.c_str(), &info) == 0 || errno != ENOENT;
}
bool preserve(const std::string& path) {
    FILE* source = fopen(path.c_str(), "rb");
    if (!source) return errno == ENOENT;
    std::string archive = path + ".evidence-XXXXXX";
    const int fd = mkstemp(archive.data());
    if (fd < 0) { fclose(source); return false; }
    bool good = true;
    char buffer[4096];
    while (const auto count = fread(buffer, 1, sizeof buffer, source)) {
        size_t done = 0;
        while (done < count) {
            const auto written = write(fd, buffer+done, count-done);
            if (written < 0 && errno == EINTR) continue;
            if (written <= 0) { good = false; break; }
            done += written;
        }
        if (!good) break;
    }
    if (ferror(source)) good = false;
    if (fclose(source)) good = false;
    if (fsync(fd)) good = false;
    if (close(fd)) good = false;
    // Sync the archive's directory without replacing or removing the source.
    if (good) good = pswaker_commit_file(archive.c_str(), archive.c_str());
    return good;
}
std::string trim(const std::string& line) {
    const auto first = line.find_first_not_of(" \t\r\n");
    return first == std::string::npos ? "" : line.substr(first, line.find_last_not_of(" \t\r\n") - first + 1);
}
constexpr const char* key = "PSWAKER_LARGE_TEXT=";
}

thread_local SaveFile* SaveFile::active_ = nullptr;
bool SaveFile::failure(const char* reason, Problem problem) {
    problem_ = problem;
    error_ = path_ + ": " + reason;
    return false;
}
bool SaveFile::check() {
    error_.clear();
    problem_ = Problem::None;
    if (testMode() == "invalid") return failure("Unreadable/unknown controlled-test marker (.test). Exit and repair or remove the marker; saves preserved.", Problem::InvalidTest);
    if (present(path_ + ".pending")) return failure("Interrupted or failed save retained (.pending). Exit or explicitly restore a valid backup.", Problem::Recovery);
    std::string bytes;
    bool exists;
    if (!readSave(path_, bytes, exists)) return failure("Cannot read save. Check storage/size/permissions, then Retry; data was preserved.", errno == EFBIG ? Problem::Recovery : Problem::Unavailable);
    if (!exists && present(path_ + ".backup")) return failure("Primary save is missing but backup data exists. Explicit recovery is required; new-game initialization is blocked.", Problem::Recovery);
    if (exists && !validSave(bytes)) return failure("Save corruption detected. Data preserved; restore a valid backup or Exit and recover on the computer.", Problem::Recovery);
    return true;
}
bool SaveFile::canRestore() const {
    if (problem_ != Problem::Recovery) return false;
    std::string bytes;
    bool exists;
    return readSave(path_ + ".backup", bytes, exists) && exists && validSave(bytes);
}
bool SaveFile::restore() {
    check();
    if (!canRestore()) return failure("No recoverable save problem with a valid backup. Repair the reported path or Exit; progress was preserved.");
    std::string bytes;
    bool exists;
    if (!readSave(path_ + ".backup", bytes, exists) || !exists || !validSave(bytes))
        return failure("No valid backup. Exit and retain the affected files for computer-side recovery.");
    // Retain both the affected primary and incomplete stage before replacement.
    if (!preserve(path_) || !preserve(path_ + ".pending")) return failure("Could not preserve affected data; restore was stopped. Repair storage and Retry.");
    if (!replace(path_, bytes)) return failure("Restore write failed or completion is uncertain. Backup and evidence retained; Retry after repair.");
    if (present(path_ + ".pending") && unlink((path_ + ".pending").c_str()))
        return failure("Restored file but could not clear interrupted stage. Repair storage and Retry.");
    // Sync removal through the existing checked replacement boundary.
    if (!replace(path_, bytes)) return failure("Restore sync failed; completion not confirmed. Backup/evidence retained.");
    return check();
}
bool SaveFile::begin() {
    if (active_ || !check()) return failure("Save blocked: unresolved earlier storage error. Exit and relaunch for recovery.");
    std::string bytes;
    bool exists;
    if (!readSave(path_, bytes, exists)) return failure("Cannot read previous completed save.");
    if (exists && (!validSave(bytes) || !replace(path_ + ".backup", bytes)))
        return failure("Could not retain previous valid backup. Saving stopped; repair storage.");
    // Create the stage exclusively. For a first save, CARDCreate initializes it.
    const int fd = open((path_ + ".pending").c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) return failure("Could not create save stage; repair storage.");
    if (close(fd) || !replace(path_ + ".pending", bytes)) return failure("Could not sync save stage; completion not confirmed.");
    active_ = this;
    testMode_ = testMode();
    if (!testMode_.empty()) fprintf(stderr, "STORAGE TEST mode=%s path=%s (owner-controlled fault injection)\n", testMode_.c_str(), path_.c_str());
    return true;
}
bool SaveFile::finish(bool completed) {
    if (active_ != this) return failure("No active save transaction.");
    if (completed && testMode_ == "hold-publish") {
        fprintf(stderr, "STORAGE TEST pending-publish hold=20s path=%s\n", path_.c_str());
        std::this_thread::sleep_for(std::chrono::seconds(20));
    }
    active_ = nullptr;
    std::string bytes;
    bool exists;
    if (!completed || !readSave(path_ + ".pending", bytes, exists) || !exists || !validSave(bytes))
        return failure("Save failed validation or a CARD write. Previous save, backup and interrupted stage retained.");
    if (!replace(path_, bytes)) return failure("Save replacement failed or completion uncertain; backup and interrupted stage retained.");
    if (unlink((path_ + ".pending").c_str())) return failure("Save stage cleanup failed; completion not confirmed.");
    // Persist removal before returning completion. Keep the backup on all paths.
    const auto parent = path_.substr(0, path_.find_last_of('/'));
    const int fd = open(parent.c_str(), O_RDONLY);
    if (fd < 0) return failure("Cannot sync save directory; completion uncertain.");
    const bool synced = fsync(fd) == 0;
    const bool closed = close(fd) == 0;
    if (!synced || !closed) return failure("Save directory sync failed; completion uncertain. Previous backup retained.");
    error_.clear();
    return true;
}
const char* SaveFile::cardPath(const char* path) {
    static thread_local std::string translated;
    if (!active_ || path != active_->path_) return path;
    translated = active_->path_ + ".pending";
    return translated.c_str();
}
std::string SaveFile::testMode() const {
    std::string bytes;
    bool exists;
    if (!readSave(path_ + ".test", bytes, exists)) return "invalid";
    if (!exists) return "";
    if (bytes == "fail-write\n") return "fail-write";
    if (bytes == "hold-publish\n") return "hold-publish";
    return "invalid";
}
bool SaveFile::rejectCardWrite(const char* path) {
    return active_ && active_->testMode_ == "fail-write" && path == active_->path_ + ".pending";
}
extern "C" const char* pswaker_gci_path(const char* path) {
    StorageHostAlloc hostAlloc;
    return SaveFile::cardPath(path);
}
namespace {
thread_local std::unique_ptr<SaveFile> gameSave;
std::string gameSavePath(int slot) {
    return std::string("/data/pswaker/saves/USA/Card ") + (slot == 0 ? "A" : "B") + "/01-GZLE-gczelda.gci";
}
bool reportSave(bool good, const SaveFile& file) {
    if (!good) fprintf(stderr, "STORAGE ERROR %s\n", file.error());
    return good;
}
}
extern "C" bool pswaker_save_begin(int slot) {
    StorageHostAlloc hostAlloc;
    fprintf(stderr, "STORAGE requested-save path=%s\n", gameSavePath(slot).c_str());
    gameSave = std::make_unique<SaveFile>(gameSavePath(slot));
    const bool good = gameSave->begin();
    return reportSave(good, *gameSave);
}
extern "C" bool pswaker_save_check(int slot) {
    StorageHostAlloc hostAlloc;
    SaveFile file(gameSavePath(slot));
    const bool good = file.check();
    return reportSave(good, file);
}
extern "C" bool pswaker_save_finish(bool completed) {
    StorageHostAlloc hostAlloc;
    if (!gameSave) return false;
    const bool good = gameSave->finish(completed);
    fprintf(stderr, "STORAGE save-completed=%d\n", good);
    return reportSave(good, *gameSave);
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
    controls_ = parse_controls(contents);
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
        if (line == "[dev]" || line == "[controls]") {
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
