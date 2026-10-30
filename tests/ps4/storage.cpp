#include "storage.hpp"
#include <cassert>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <string>
#include <unistd.h>
#include <sys/wait.h>

namespace fs = std::filesystem;
namespace {
bool failSync = false, failRename = false, failClose = false;
int syncCountdown = -1;
std::string read(const fs::path& path) {
    std::ifstream file(path);
    return {std::istreambuf_iterator<char>(file), {}};
}
void write(const fs::path& path, const std::string& data) { std::ofstream(path) << data; }
}
extern "C" int __real_fsync(int);
extern "C" int __wrap_fsync(int fd) {
    if (failSync || syncCountdown == 0) { errno = EIO; return -1; }
    if (syncCountdown > 0) --syncCountdown;
    return __real_fsync(fd);
}
extern "C" int __real_rename(const char*, const char*);
extern "C" int __wrap_rename(const char* from, const char* to) {
    if (failRename) { errno = EIO; return -1; }
    return __real_rename(from, to);
}
extern "C" int __real_close(int);
extern "C" int __wrap_close(int fd) {
    const int result = __real_close(fd);
    if (failClose) { errno = EIO; return -1; }
    return result;
}
int main(int argc, char** argv) {
    assert(argc == 3);
    const fs::path root = fs::path(argv[2]) / "user";
    PortSettings settings(root.string());
    if (std::strcmp(argv[1], "unavailable") == 0) {
        fs::create_directories(root / "saves/USA");
        write(root / "saves/USA/Card A", "preserve me");
        assert(!settings.check());
        assert(std::strstr(settings.error(), "Card A"));
        assert(read(root / "saves/USA/Card A") == "preserve me");
        fs::rename(root / "saves/USA/Card A", root / "preserved");
        assert(settings.check());
        assert(read(root / "preserved") == "preserve me");
        return 0;
    }
    assert(settings.check());
    if (std::strcmp(argv[1], "controls-child") == 0) {
        assert(!settings.largeText() && !*settings.controlsFeedback());
        assert(settings.controls().binding(GameAction::A) == ControlTarget::L3);
        assert(settings.controls().binding(GameAction::Start) == ControlTarget::Circle);
        assert(settings.controls().invertCameraX && settings.controls().invertCameraY);
        return 0;
    }
    if (std::strcmp(argv[1], "child") == 0) {
        assert(!settings.largeText());
        return 0;
    }
    const auto ini = root / "settings.ini";
    if (std::strcmp(argv[1], "controls-profile-repair") == 0) {
        auto pending = ControlsConfig::defaults();
        assert(pending.assign(GameAction::Start, ControlTarget::L1));
        pending.invertCameraX = true;
        const std::string prefix = "; owner settings\r\nPSWAKER_LARGE_TEXT=0\r\n";
        const std::string other = "[audio]\r\nvolume=37\r\n";
        const std::string dev = "[dev]\r\nCOS_FPS60=1\r\n";
        const auto section = serialize_controls(pending);
        const auto apply = [&](const std::string& before, const std::string& expected) {
            write(ini, before);
            assert(settings.check());
            assert(settings.setControls(pending));
            assert(read(ini) == expected && !*settings.controlsFeedback());
            PortSettings reloaded(root.string());
            assert(reloaded.check() && reloaded.controls() == pending && !*reloaded.controlsFeedback());
        };
        apply("[controls]\nversion=9\nPSWAKER_LARGE_TEXT=0\nCOS_AUDIO=on\n" + dev,
              "PSWAKER_LARGE_TEXT=0\nCOS_AUDIO=on\n" + section + dev);
        PortSettings repaired(root.string());
        assert(repaired.check() && !repaired.largeText());
        apply(prefix + other + dev, prefix + other + section + dev); // Missing section.
        apply(prefix + "[controls\nversion=9\nA=Touchpad\n" + other + dev,
              prefix + other + section + dev); // Malformed controls are repaired only on Apply.
        apply(prefix + "[controls]\nversion=9\n[controls]\nA=Share\n" + other + dev,
              prefix + other + section + dev); // Duplicate sections are replaced as a whole.
        apply(prefix + "[controls]\nversion=9\n; keep this comment\r\nOTHER=37\r\n" + other + dev,
              prefix + "; keep this comment\r\nOTHER=37\r\n" + other + section + dev);
        apply(prefix + dev + "[controls]\nversion=9\n", prefix + section + dev);
        apply("# legacy without final newline", "# legacy without final newline\n" + section);
        fs::remove(ini);
        assert(settings.setControls(pending) && read(ini) == section);
        return 0;
    }
    if (std::strcmp(argv[1], "controls-failures") == 0) {
        const std::string previous = "PSWAKER_LARGE_TEXT=0\n[dev]\nCOS_FPS60=1\n";
        write(ini, previous);
        assert(settings.check());
        auto pending = ControlsConfig::defaults();
        assert(pending.assign(GameAction::A, ControlTarget::L3));
        pending.invertCameraY = true;
        for (bool* fault : {&failSync, &failClose, &failRename}) {
            *fault = true;
            assert(!settings.setControls(pending));
            *fault = false;
            assert(settings.controls() == ControlsConfig::defaults() && !settings.largeText());
            assert(*settings.error() && read(ini) == previous);
        }
        auto invalid = pending;
        invalid.bindings[0] = invalid.bindings[1];
        assert(!settings.setControls(invalid) && read(ini) == previous);
        syncCountdown = 2;
        assert(!settings.setControls(pending));
        syncCountdown = -1;
        assert(settings.controls() == ControlsConfig::defaults() && *settings.error());
        PortSettings reopened(root.string());
        assert(reopened.check() && reopened.controls() == pending); // Disk may already contain the replacement.
        assert(settings.setControls(pending)); // Retry writes the whole pending snapshot again.
        assert(settings.controls() == pending && !*settings.error());
        return 0;
    }
    if (std::strcmp(argv[1], "controls-apply") == 0) {
        const std::string prefix = "# owner settings\r\nPSWAKER_LARGE_TEXT=0\r\nCOS_AUDIO=on\r\n";
        const std::string tail = "[dev]\r\nCOS_FPS60=1\r\n";
        auto custom = ControlsConfig::defaults();
        custom.bindings = {ControlTarget::L3, ControlTarget::R3, ControlTarget::L1,
            ControlTarget::Options, ControlTarget::Cross, ControlTarget::Circle};
        custom.invertCameraX = custom.invertCameraY = true;
        write(ini, prefix + serialize_controls(ControlsConfig::defaults()) + tail);
        assert(settings.check());
        assert(settings.setControls(custom));
        assert(settings.controls() == custom && !settings.largeText());
        assert(read(ini) == prefix + serialize_controls(custom) + tail);
        const pid_t child = fork();
        assert(child >= 0);
        if (child == 0) { execl(argv[0], argv[0], "controls-child", argv[2], nullptr); _exit(99); }
        int status = 0;
        assert(waitpid(child, &status, 0) == child && WIFEXITED(status) && WEXITSTATUS(status) == 0);
        return 0;
    }
    if (std::strcmp(argv[1], "controls-roundtrip") == 0) {
        const std::string controls = "[controls]\r\nversion=1\r\nA=L3\r\nB=R3\r\nX=L1\r\nY=Options\r\nZ=Cross\r\nStart=Circle\r\n"
            "invert_camera_x=1\r\ninvert_camera_y=1\r\n";
        const std::string tail = "[dev]\nCOS_FPS60=1\n";
        write(ini, "# owner settings\nCOS_AUDIO=on\n" + controls + tail);
        assert(settings.check());
        assert(settings.setLargeText(false));
        assert(read(ini) == "# owner settings\nCOS_AUDIO=on\nPSWAKER_LARGE_TEXT=0\n" + controls + tail);
        const pid_t child = fork();
        assert(child >= 0);
        if (child == 0) { execl(argv[0], argv[0], "controls-child", argv[2], nullptr); _exit(99); }
        int status = 0;
        assert(waitpid(child, &status, 0) == child && WIFEXITED(status) && WEXITSTATUS(status) == 0);
        return 0;
    }
    if (std::strcmp(argv[1], "invalid") == 0) {
        write(ini, "PSWAKER_LARGE_TEXT=invalid\n");
        assert(!settings.check());
        assert(!settings.setLargeText(false));
        assert(read(ini) == "PSWAKER_LARGE_TEXT=invalid\n");
        fs::remove(ini); fs::create_directory(ini);
        assert(!settings.check());
        assert(!settings.setLargeText(false));
        assert(fs::is_directory(ini));
        return 0;
    }
    const std::string previous = "# owner settings\nCOS_AUDIO=on\n[dev]\nCOS_FPS60=1\n";
    write(ini, previous);
    assert(settings.check());
    assert(settings.largeText());
    if (std::strcmp(argv[1], "uncertain-completion") == 0) {
        syncCountdown = 2; // File + pre-rename directory sync pass; post-rename fails.
        assert(!settings.setLargeText(false));
        assert(settings.largeText() && *settings.error());
        syncCountdown = -1;
        PortSettings reopened(root.string());
        assert(reopened.check() && !reopened.largeText());
        return 0;
    }
    if (std::strcmp(argv[1], "failed-replacement") == 0) {
        for (bool* failure : {&failSync, &failClose, &failRename}) {
            *failure = true;
            assert(!settings.setLargeText(false));
            *failure = false;
            assert(settings.largeText());
            assert(read(ini) == previous);
            assert(*settings.error());
        }
        assert(settings.setLargeText(false));
        return 0;
    }
    assert(settings.setLargeText(false));
    assert(!settings.largeText());
    assert(read(ini) == "# owner settings\nCOS_AUDIO=on\nPSWAKER_LARGE_TEXT=0\n[dev]\nCOS_FPS60=1\n");
    const pid_t child = fork();
    assert(child >= 0);
    if (child == 0) { execl(argv[0], argv[0], "child", argv[2], nullptr); _exit(99); }
    int status = 0;
    assert(waitpid(child, &status, 0) == child && WIFEXITED(status) && WEXITSTATUS(status) == 0);
}
