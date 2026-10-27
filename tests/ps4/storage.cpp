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
    if (std::strcmp(argv[1], "child") == 0) {
        assert(!settings.largeText());
        return 0;
    }
    const auto ini = root / "settings.ini";
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
