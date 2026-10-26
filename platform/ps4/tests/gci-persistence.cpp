#include "card/CardGciFolder.hpp"
#include <aurora/aurora.h>
#include <array>
#include <cassert>
#include <cerrno>
#include <cstring>
#include <fstream>
#include <string>

// GPU/application logging is outside the storage boundary; SDL I/O is real.
namespace aurora {
AuroraConfig g_config{};
void log_internal(AuroraLogLevel, const char*, const char*, unsigned) noexcept {}
}
namespace {
bool failSync = false, failRename = false;
std::string read(const std::filesystem::path& path) {
    std::ifstream stream(path, std::ios::binary);
    return {std::istreambuf_iterator<char>(stream), {}};
}
}
extern "C" int __real_fsync(int);
extern "C" int __wrap_fsync(int fd) {
    if (failSync) { errno = EIO; return -1; }
    return __real_fsync(fd);
}
extern "C" int __real_rename(const char*, const char*);
extern "C" int __wrap_rename(const char* from, const char* to) {
    if (failRename) { errno = EIO; return -1; }
    return __real_rename(from, to);
}
int main(int argc, char** argv) {
    assert(argc == 3);
    using namespace aurora::card;
    const std::filesystem::path folder(argv[2]);
    const auto path = folder / "01-GZLE-gczelda.gci";
    CardGciFolder card;
    card.InitCard("GZLE", "01");
    assert(card.open(folder));
    FileHandle file;
    assert(card.createFile("gczelda", BlockSize, file) == ECardResult::READY);
    const char progress[] = "Synthetic Link: completed Outset";
    assert(card.fileWrite(file, progress, sizeof progress) == ECardResult::READY);
    CardStat metadata{};
    assert(card.getStatus(file, metadata) == ECardResult::READY);
    metadata.x30_iconAddr = 0;
    assert(card.setStatus(file, metadata) == ECardResult::READY);
    assert(card.commit() == ECardResult::READY);
    const auto previous = read(path);
    if (std::strcmp(argv[1], "roundtrip")) {
        failSync = !std::strcmp(argv[1], "sync-failure");
        failRename = !std::strcmp(argv[1], "rename-failure");
        const char changed[] = "UNCONFIRMED newer progress";
        assert(card.fileWrite(file, changed, sizeof changed) == ECardResult::IOERROR);
        assert(read(path) == previous);
        // Metadata replacement must propagate the same failure.
        metadata.x30_iconAddr = 128;
        assert(card.setStatus(file, metadata) == ECardResult::READY);
        assert(card.commit() == ECardResult::IOERROR);
        assert(read(path) == previous);
        failSync = failRename = false;
    }
    card.close();
    assert(card.open(folder));
    assert(card.openFile("gczelda", file) == ECardResult::READY);
    char restored[sizeof progress]{};
    assert(card.fileRead(file, restored, sizeof restored) == ECardResult::READY);
    assert(std::memcmp(restored, progress, sizeof progress) == 0);
    assert(card.getStatus(file, metadata) == ECardResult::READY);
    assert(metadata.x30_iconAddr == 0);
}
