#!/usr/bin/env python3
"""Capture actual source closure and host/package provenance, not hardware results."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve()


def output(*args):
    return subprocess.check_output(args, text=True).strip()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


closure = {"mesa_revision": output("git", "-C", str(root / "src/mesa"), "rev-parse", "HEAD"),
           "libdrm_revision": output("git", "-C", str(root / "src/libdrm"), "rev-parse", "HEAD"),
           "host_versions": {tool: output(*command) for tool, command in {
               "clang": ["clang-21", "--version"], "cmake": ["cmake", "--version"],
               "ninja": ["ninja", "--version"], "dotnet": ["dotnet", "--info"],
               "python": ["python3", "--version"]}.items()},
           "host_packages": output("dpkg-query", "-W"), "dawn_deps": [],
           "sdk_package_metadata": [], "cmake_downloads": [], "nuget_locks": []}
for directory, children, files in os.walk(root / "src/dawn/third_party"):
    if ".git" in children or ".git" in files:
        repo = Path(directory)
        closure["dawn_deps"].append({"path": repo.relative_to(root).as_posix(),
            "revision": output("git", "-C", str(repo), "rev-parse", "HEAD"),
            "origin": output("git", "-C", str(repo), "remote", "get-url", "origin")})
        if ".git" in children:
            children.remove(".git")
for path in sorted((root / "downloads/pacbrew").glob("*")):
    if path.suffix in {".PKGINFO", ".BUILDINFO"}:
        closure["sdk_package_metadata"].append({"filename": path.name, "sha256": digest(path), "text": path.read_text()})
for path in sorted((root / "build/probe/_deps").rglob("*")):
    if path.is_file() and (path.name.endswith("-urlinfo.txt") or
                           ("-subbuild" in str(path) and path.name.endswith((".zip", ".tar.gz", ".tar.xz")))):
        closure["cmake_downloads"].append({"path": path.relative_to(root).as_posix(), "sha256": digest(path),
            **({"text": path.read_text()} if path.name.endswith("-urlinfo.txt") else {})})
for path in sorted((root / "src/liborbispkg").rglob("packages.lock.json")):
    closure["nuget_locks"].append({"path": path.relative_to(root).as_posix(), "sha256": digest(path), "text": path.read_text()})
(root / "evidence/input-closure.json").write_text(json.dumps(closure, indent=2) + "\n")
print("Recorded actual host, SDK metadata, Dawn DEPS, CMake archives and NuGet closure.")
