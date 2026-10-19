#!/usr/bin/env python3
"""Fetch only disc-free platform inputs at the map's selected source pins."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("sdk", Path(__file__).with_name("lock-sdk.py"))
sdk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sdk)

SOURCES = [
    ("refs/dusklight", "BgbrhrWatchinOVO/dusklight-ps4", "fd483cf5d4f04b0f4d887ff412d0e8691925de08"),
    ("refs/DolphinPS4", "iHaiDeeZ/DolphinPS4", "b1879cc0267a2a4f0949d7b80478fcf2abca24f6"),
    ("src/aurora", "mshivam019/dusklight-ps5", "e281999cdb4fee6127525a9a9e97979480db4bf3"),
    ("src/dawn", "mshivam019/dusklight-ps5", "652a3104791369cd23605856fbc041375ccda875"),
    ("src/sdl3", "mshivam019/dusklight-ps5", "68159af2b34cc4fe5b3548faa89e87a69e4d2dce"),
    ("src/abseil", "mshivam019/dusklight-ps5", "5c695e68fcd3e7483ed300b6591d1ec49ae37cf4"),
    ("src/liborbispkg", "OpenOrbis/LibOrbisPkg", "594021fdc435409f755a6ae0781b65ec6cec846c"),
]


def source(root, relative, repository, revision):
    cache = root / "downloads" / (relative.replace("/", "-") + ".tar.gz")
    tree = root / relative
    url = f"https://api.github.com/repos/{repository}/tarball/{revision}"
    if not cache.exists():
        sdk.download(url, cache.with_suffix(".part"))
        cache.with_suffix(".part").replace(cache)
    lockfile = Path(__file__).with_name("sources.lock.json")
    if lockfile.exists():
        wanted = {item["revision"]: item["archive_sha256"] for item in json.loads(lockfile.read_text())}
        if sdk.sha256(cache) != wanted[revision]:
            raise ValueError("Source archive digest mismatch: " + relative)
    record = {"path": relative, "repository": repository, "revision": revision,
              "archive_url": url, "archive_sha256": sdk.sha256(cache)}
    if not tree.exists():
        tree.mkdir(parents=True)
        subprocess.run(["tar", "-xf", str(cache), "-C", str(tree), "--strip-components=1"], check=True)
    print("Prepared " + relative + " at " + revision, flush=True)
    return record


def llvm(root):
    name = "llvm-project-21.1.6.src.tar.xz"
    url = "https://github.com/llvm/llvm-project/releases/download/llvmorg-21.1.6/" + name
    expected = "ae67086eb04bed7ca11ab880349b5f1ab6f50e1b88cda376eaf8a845b935762b"
    archive = root / "downloads" / name
    if not archive.exists():
        sdk.download(url, archive.with_suffix(".part"))
        archive.with_suffix(".part").replace(archive)
    if sdk.sha256(archive) != expected:
        raise ValueError("LLVM release digest mismatch")
    tree = root / "src" / "llvm-project-21.1.6.src"
    if not tree.exists():
        (root / "src").mkdir(exist_ok=True)
        parts = ["runtimes", "libcxx", "libcxxabi", "libunwind", "libc", "cmake",
                 "llvm/cmake", "llvm/utils/lit", "llvm/utils/llvm-lit", "third-party"]
        subprocess.run(["tar", "-xJf", str(archive), "-C", str(root / "src"),
                        *["llvm-project-21.1.6.src/" + p for p in parts]], check=True)
    return {"path": "src/llvm-project-21.1.6.src", "revision": "a832a5222e489298337fbb5876f8dcaf072c5cca",
            "archive_url": url, "archive_sha256": expected}


def patch(root, tree, name, directory=None):
    marker = root / tree / (".pswaker-" + name)
    if marker.exists():
        return
    command = ["git", "apply"]
    # git apply outside a repo accepts a patch against the current directory.
    work = root / tree
    if directory:
        work /= directory
    subprocess.run(command + [str(root / "refs/dusklight/patches" / name)], cwd=work, check=True)
    marker.touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    (root / "downloads").mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(source, root, *item) for item in SOURCES]
        futures.append(pool.submit(llvm, root))
        records = [f.result() for f in futures]
    (root / "evidence/source-archives.json").write_text(json.dumps(records, indent=2) + "\n")
    for tree, name in [("refs/DolphinPS4", "dolphinps4-ps4-runtime.patch"),
                       ("src/aurora", "aurora-ps4.patch"),
                       ("src/dawn", "dawn-ps4.patch"),
                       ("src/sdl3", "sdl3-ps4.patch"),
                       ("src/abseil", "abseil-ps4.patch"),
                       ("src/liborbispkg", "liborbispkg-ps4-dusklight.patch")]:
        patch(root, tree, name)
    shutil.copyfile(root / "refs/dusklight/tools/ac_ps4_drm.c", root / "refs/DolphinPS4/port/mesa/ac_ps4_drm.c")
    patch(root, "src/llvm-project-21.1.6.src", "libcxx-ps4-atomic-wait.patch", "libcxx/src")
    native = root / "src/native-platform"
    native.mkdir(exist_ok=True)
    if not (native / "ps4/native/platform.c").exists():
        subprocess.run(["git", "apply", "--include=ps4/native/platform.c", "--include=ps4/native/platform.h",
                        "--include=ps4/native/realpath.c", "--include=ps4/input.cpp",
                        str(root / "refs/dusklight/patches/dusklight-ps4.patch")], cwd=native, check=True)
        platform = native / "ps4/native/platform.c"
        platform.write_text(platform.read_text().replace('"/data/dusklight-ps4"', '"/data/pswaker-diagnostic-prototype"')
                            .replace('"/dusklight.log"', '"/platform.log"')
                            .replace('"/dusklight.prev.log"', '"/platform.prev.log"'))
    print("Selected source patches applied. Dawn DEPS, Mesa and libdrm still require preparation.")
