#!/usr/bin/env python3
"""Throwaway diagnostic: freeze and fetch the selected PacBrew SDK inputs.

The database is used only by `freeze`; `fetch` reads the committed lock.
Archives are verified before extraction. No game files or keys are used.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

import build_inputs

BASE = "https://pacman.mydedibox.fr/pacbrew/packages"
PACKAGES = "clang headers musl libcxx vars create-fself create-gp4 pkgtools orbis-lib-gen readoelf pkg-config zlib libpng bzip2".split()
PLATFORM = build_inputs.Locations().platform


def download(url, path):
    subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                    "--connect-timeout", "20", "--max-time", "1800", "--retry", "2",
                    url, "--output", str(path)], check=True)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def freeze(database, output):
    records = {}
    with tarfile.open(database) as archive:
        for member in archive:
            if not member.name.endswith("/desc"):
                continue
            fields = {}
            for block in archive.extractfile(member).read().decode().split("\n\n"):
                lines = block.strip().splitlines()
                if len(lines) > 1:
                    fields[lines[0].strip("%")] = lines[1:]
            name = fields.get("NAME", [""])[0]
            if name not in ["ps4-openorbis-" + item for item in PACKAGES]:
                continue
            if name in records:
                raise ValueError("Ambiguous package: " + name)
            records[name] = {"name": name, "version": fields["VERSION"][0],
                             "filename": fields["FILENAME"][0],
                             "sha256": fields["SHA256SUM"][0],
                             "bytes": int(fields["CSIZE"][0]),
                             "project_url": fields.get("URL", []),
                             "declared_license": fields.get("LICENSE", []),
                             "dependencies": fields.get("DEPENDS", []),
                             "source_revision": None}
    ordered = [records["ps4-openorbis-" + item] for item in PACKAGES]
    lock = {"repository": BASE, "database_sha256": sha256(database),
            "source_revision_note": "Package database does not identify immutable source revisions. Inspect package build metadata; do not infer revisions from versions.",
            "packages": ordered}
    output.write_text(json.dumps(lock, indent=2) + "\n")
    print(f"Locked {len(ordered)} packages ({sum(p['bytes'] for p in ordered)} bytes)")


def fetch_one(package, cache, base):
    filename = package["filename"]
    if Path(filename).name != filename:
        raise ValueError("Invalid archive filename")
    target = cache / filename
    if not target.exists() or sha256(target) != package["sha256"]:
        temporary = target.with_suffix(target.suffix + ".part")
        download(base + "/" + filename, temporary)
        if sha256(temporary) != package["sha256"]:
            raise ValueError("SHA-256 mismatch: " + filename)
        temporary.replace(target)
    print("Verified " + filename, flush=True)
    return target


def fetch(lockfile, root):
    lock = json.loads(lockfile.read_text())
    cache = root / "downloads" / "pacbrew"
    sdk = root / "sdk"
    cache.mkdir(parents=True, exist_ok=True)
    sdk.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        archives = list(pool.map(lambda p: fetch_one(p, cache, lock["repository"]), lock["packages"]))
    for package, path in zip(lock["packages"], archives):
        with tarfile.open(path) as archive:
            for metadata in (".PKGINFO", ".BUILDINFO"):
                members = [m for m in archive.getmembers() if m.name.removeprefix("./") == metadata]
                for member in members:
                    (cache / (package["filename"] + metadata)).write_bytes(archive.extractfile(member).read())
            members = [m for m in archive.getmembers()
                       if m.name.removeprefix("./") not in {".PKGINFO", ".BUILDINFO", ".MTREE", ".INSTALL"}]
            archive.extractall(sdk, members=members, filter="data")
    # Match the reference's text-only prefix relocation, without modifying headers/binaries.
    prefix = sdk / "opt" / "pacbrew"
    for path in prefix.rglob("*"):
        if not path.is_file() or path.is_symlink() or "include" in path.relative_to(prefix).parts:
            continue
        content = path.read_bytes()
        if b"\0" not in content and b"/opt/pacbrew" in content:
            path.write_bytes(content.replace(b"/opt/pacbrew", str(prefix).encode()))
    print("SDK extracted: " + str(prefix / "ps4" / "openorbis"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("database", type=Path)
    freeze_parser.add_argument("--output", type=Path, default=PLATFORM / "sdk.lock.json")
    fetch_parser = sub.add_parser("fetch")
    fetch_parser.add_argument("root", type=Path)
    fetch_parser.add_argument("--lock", type=Path, default=PLATFORM / "sdk.lock.json")
    args = parser.parse_args()
    if args.action == "freeze":
        freeze(args.database, args.output)
    else:
        fetch(args.lock, args.root.resolve())
