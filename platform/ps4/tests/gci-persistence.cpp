#include "card/CardGciFolder.hpp"
#include <aurora/aurora.h>
#include <array>
#include <cassert>
#include <cerrno>
#include <cstring>
#include <fstream>
#include <string>
#include "storage.hpp"

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
    if (!std::strcmp(argv[1], "transaction") || std::string(argv[1]).starts_with("corrupt") ||
        !std::strcmp(argv[1], "missing-primary") || !std::strcmp(argv[1], "controlled-failure")) {
        // A new save spans multiple real CARD calls. Failed later writes must
        // leave the completed primary intact, even if earlier writes succeeded.
        SaveFile save(path.string());
        assert(save.check());
        assert(save.begin());
        CardGciFolder staged;
        staged.InitCard("GZLE", "01");
        assert(staged.open(folder));
        FileHandle handle;
        assert(staged.createFile("gczelda", 0x18000, handle) == ECardResult::READY);
        // Independently constructed USA save blocks with valid slot checksums.
        std::array<unsigned char, 0x18000> data{};
        for (size_t block : {0x2000u, 0x4000u}) {
            for (size_t slot = 0; slot < 3; ++slot) {
                const size_t checksum = block + 8 + slot * 0x770 + 0x768;
                data[checksum + 4] = 0xff; data[checksum + 5] = 0xff;
                data[checksum + 6] = 0xf8; data[checksum + 7] = 0x98;
            }
            unsigned sum = 0, inverse = 0;
            for (size_t i = 0; i < 0x1ffc; i += 2) {
                unsigned word = (data[block+i] << 8) | data[block+i+1];
                sum += word; inverse += word ^ 0xffff;
            }
            data[block+0x1ffc] = sum >> 8; data[block+0x1ffd] = sum;
            data[block+0x1ffe] = inverse >> 8; data[block+0x1fff] = inverse;
        }
        assert(staged.fileWrite(handle, data.data(), data.size()) == ECardResult::READY);
        assert(save.finish(true));
        const auto completed = read(path);
        assert(!completed.empty());
        if (!std::strcmp(argv[1], "controlled-failure")) {
            { std::ofstream marker(path.string() + ".test"); marker << "fail-write\n"; }
            assert(save.testMode() == "fail-write");
            assert(save.begin());
            const char newer[] = "unconfirmed";
            assert(staged.fileWrite(handle, newer, sizeof newer) == ECardResult::IOERROR);
            assert(!save.finish(false));
            assert(read(path) == completed);
            return 0;
        }
        assert(save.begin());
        if (!std::strcmp(argv[1], "missing-primary")) {
            assert(save.finish(true));
            std::filesystem::remove(path);
            assert(!save.check());
            assert(save.canRestore());
            assert(save.restore());
            assert(read(path) == completed);
            return 0;
        }
        if (std::string(argv[1]).starts_with("corrupt")) {
            // Finish a second save to establish a previous valid backup.
            assert(save.finish(true));
            std::string damaged = completed;
            damaged[0x2048] ^= 1;
            if (!std::strcmp(argv[1], "corrupt-size")) damaged.append(8192, 'X');
            { std::ofstream out(path, std::ios::binary); out.write(damaged.data(), damaged.size()); }
            const bool noBackup = !std::strcmp(argv[1], "corrupt-no-backup");
            if (noBackup) std::filesystem::remove(path.string() + ".backup");
            assert(!save.check());
            assert(save.canRestore() == !noBackup);
            assert(read(path) == damaged); // Checking/declining never resets data.
            if (noBackup) {
                assert(!save.restore());
                assert(read(path) == damaged);
            } else {
                assert(save.restore());
                assert(save.check() && read(path) == completed);
                bool originalRetained = false;
                for (const auto& entry : std::filesystem::directory_iterator(folder))
                    if (entry.path().filename().string().starts_with("01-GZLE-gczelda.gci.evidence-"))
                        originalRetained |= read(entry.path()) == damaged;
                assert(originalRetained);
            }
            return 0;
        }
        const char changed[] = "partial newer save";
        assert(staged.fileWrite(handle, changed, sizeof changed) == ECardResult::READY);
        assert(read(path) == completed);
        failSync = true;
        assert(staged.fileWrite(handle, changed, sizeof changed) == ECardResult::IOERROR);
        assert(!save.finish(false));
        failSync = false;
        assert(read(path) == completed);
        SaveFile relaunched(path.string());
        assert(!relaunched.check());
        assert(relaunched.canRestore());
        // Declining does not change either primary or interrupted data.
        const auto pending = read(path.string() + ".pending");
        assert(!relaunched.check());
        assert(read(path) == completed && read(path.string() + ".pending") == pending);
        assert(relaunched.restore());
        assert(relaunched.check());
        assert(read(path) == completed);
        return 0;
    }
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
