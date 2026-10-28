// Throwaway runtime build preflight. This is NOT the complete hardware diagnostic.
// No game code, assets, keys, graphics, audio or controller coverage.
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <mutex>
#include <pthread.h>
#include <sys/stat.h>
#include <thread>
#include <unistd.h>

namespace {
FILE* log_file;
int failures;
int constructed;
struct ConstructorProbe { ConstructorProbe() { constructed = 37; } } constructor_probe;
std::atomic<int> tls_destroyed{0};
struct ThreadProbe { int value = 0; ~ThreadProbe() { ++tls_destroyed; } };
thread_local ThreadProbe thread_probe;
pthread_once_t once = PTHREAD_ONCE_INIT;
std::atomic<int> once_count{0};

void stage(const char* name) {
  // Flush before each operation, including any operation that could hang or crash.
  std::fprintf(log_file, "STAGE %s\n", name);
  std::fflush(log_file);
  if (fsync(fileno(log_file)) != 0) {
    std::fprintf(log_file, "FAIL log-fsync\n");
    ++failures;
  }
}
void check(bool ok, const char* name) {
  std::fprintf(log_file, "%s %s\n", ok ? "PASS" : "FAIL", name);
  if (!ok) ++failures;
  std::fflush(log_file);
}
void initialize_once() { ++once_count; }
}

int main() {
  constexpr const char* root = "/data/pswaker-diagnostic-prototype";
  mkdir(root, 0777);
  log_file = std::fopen("/data/pswaker-diagnostic-prototype/runtime-preflight.log", "a");
  if (!log_file) return 1;
  std::fprintf(log_file, "BEGIN runtime build preflight; incomplete diagnostic\n");
  stage("constructors");
  check(constructed == 37, "static-constructor");

  stage("tls-and-once");
  thread_probe.value = 99;
  std::atomic<int> worker_errors{0};
  auto worker = [&worker_errors](int value) {
    if (thread_probe.value != 0) ++worker_errors;
    thread_probe.value = value;
    if (pthread_once(&once, initialize_once) != 0) ++worker_errors;
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    if (thread_probe.value != value) ++worker_errors;
  };
  std::thread first(worker, 11), second(worker, 22);
  first.join(); second.join();
  check(worker_errors == 0 && thread_probe.value == 99, "thread-local-isolation");
  check(tls_destroyed == 2, "thread-local-destructors");
  check(once_count == 1, "pthread-once");

  stage("mutex-condition-variable");
  std::mutex mutex;
  std::condition_variable condition;
  bool ready = false;
  std::thread notifier([&] {
    std::lock_guard lock(mutex);
    ready = true;
    condition.notify_one();
  });
  {
    std::unique_lock lock(mutex);
    check(condition.wait_for(lock, std::chrono::seconds(2), [&] { return ready; }), "condition-variable");
  }
  notifier.join();

  stage("atomic-wait-notify");
  std::atomic<int> signal{0};
  std::thread sender([&] {
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    signal.store(1);
    signal.notify_all();
  });
  signal.wait(0);
  sender.join();
  check(signal == 1, "atomic-wait-notify");

  stage("file-replacement");
  constexpr const char* state = "/data/pswaker-diagnostic-prototype/preflight-state.txt";
  constexpr const char* temporary = "/data/pswaker-diagnostic-prototype/preflight-state.tmp";
  int previous = 0;
  if (FILE* input = std::fopen(state, "r")) {
    check(std::fscanf(input, "%d", &previous) == 1 && previous > 0, "previous-launch-state");
    check(std::fclose(input) == 0, "state-read-close");
  } else {
    std::fprintf(log_file, "OBSERVATION no previous-launch state; expected only on initial run\n");
  }
  if (FILE* output = std::fopen(temporary, "w")) {
    const bool wrote = std::fprintf(output, "%d\n", previous + 1) > 0;
    const bool flushed = std::fflush(output) == 0;
    const bool synced = fsync(fileno(output)) == 0;
    const bool closed = std::fclose(output) == 0;
    check(wrote && flushed && synced && closed, "state-write-flush-sync-close");
    if (wrote && flushed && synced && closed) check(std::rename(temporary, state) == 0, "state-rename");
  } else check(false, "state-open");
  std::fprintf(log_file, "END failures=%d launch=%d; hardware gate remains incomplete\n", failures, previous + 1);
  std::fflush(log_file);
  const bool synced = fsync(fileno(log_file)) == 0;
  const bool closed = std::fclose(log_file) == 0;
  return failures || !synced || !closed ? 1 : 0;
}
