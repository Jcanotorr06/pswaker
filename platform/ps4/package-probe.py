#!/usr/bin/env python3
"""Package this bounded diagnostic with a source-built, pinned LibOrbisPkg."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent


def run(command, **kwargs):
    subprocess.run(command, check=True, **kwargs)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def identity():
    value = hashlib.sha256()
    for path in sorted(HERE.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".md"} or any(part in {'evidence', 'tests'} for part in path.relative_to(HERE).parts):
            continue
        value.update(path.relative_to(HERE).as_posix().encode() + b"\0" + path.read_bytes())
    for command in (["clang-21", "--version"], ["cmake", "--version"], ["ninja", "--version"], ["dotnet", "--version"]):
        value.update(subprocess.check_output(command))
    return value.hexdigest()[:20]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--identity-only", action="store_true")
    parser.add_argument("--app-version", default="01.04", help="Maintained diagnostic SFO version")
    args = parser.parse_args()
    if not re.fullmatch(r"\d{2}\.\d{2}", args.app_version):
        parser.error("--app-version must be NN.NN")
    if args.identity_only:
        print(identity())
        raise SystemExit(0)
    root = args.root.resolve()
    sdk = root / "sdk/opt/pacbrew/ps4/openorbis"
    env = dict(os.environ, OPENORBIS=str(sdk), OO_PS4_TOOLCHAIN=str(sdk),
               PS4_PORT_ROOT=str(root), DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1",
               DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1", NUGET_PACKAGES=str(root / "nuget-packages"))
    tool_source = root / "src/liborbispkg"
    sdk_version = subprocess.check_output(["dotnet", "--version"], text=True).strip()
    (tool_source / "global.json").write_text(json.dumps({"sdk": {"version": sdk_version, "rollForward": "disable"}}))
    for project in ['LibOrbisPkg.Core', 'PkgTool.Core']:
        lock = 'PkgTool.Core.packages.lock.json' if project == 'PkgTool.Core' else 'packages.lock.json'
        shutil.copyfile(HERE / 'provenance/nuget' / lock, tool_source / project / 'packages.lock.json')
    with (root / "evidence/pkgtool-build.log").open("w") as log:
        run(["dotnet", "publish", "PkgTool.Core/PkgTool.Core.csproj", "-c", "Release",
             "--self-contained", "false", "-p:RestoreLockedMode=true", "-p:RestorePackagesWithLockFile=true",
             "-o", str(root / "build/pkgtool")], cwd=tool_source, env=env, stdout=log, stderr=subprocess.STDOUT)
    run(["python3", str(HERE / "capture-inputs.py"), str(root)])
    output = root / "out"
    stage = root / "build/probe-stage"
    (stage / "sce_sys").mkdir(parents=True, exist_ok=True)
    executable = root / "build/probe/platform_diagnostic_eboot/eboot.bin"
    shutil.copyfile(executable, stage / "eboot.bin")
    shutil.copyfile(root / "refs/DolphinPS4/sce_sys/icon0.png", stage / "sce_sys/icon0.png")
    manifest = {"diagnostic_build_id": identity(), "app_version": args.app_version,
                "hardware_status": "Not tested on a console; historical 01.02 results do not validate this artifact",
                "diagnostic_scope": "Disc-free platform evidence only; not game correctness or performance",
                "sources": json.loads((root / "evidence/source-archives.json").read_text()),
                "sdk": json.loads((HERE / "sdk.lock.json").read_text()),
                "local_adaptations": json.loads((root / "evidence/local-adaptations.json").read_text()),
                "input_closure": json.loads((root / "evidence/input-closure.json").read_text()),
                "patch_series": json.loads((HERE / "patch-series.json").read_text()),
                "renderer_reconciliation": json.loads((root / "evidence/renderer-reconciliation.json").read_text()),
                "dependency_lock": json.loads((HERE / "dependencies.lock.json").read_text()),
                "dotnet_sdk": sdk_version, "eboot_sha256": digest(executable),
                "owner_reported_baseline": {"console": "PS4 Slim", "firmware": "9.00", "homebrew": "GoldHEN v2.4b18", "status": "Confirm for each hardware run; not queried by the app"}}
    manifest_file = stage / "build-info.json"
    manifest_file.write_text(json.dumps(manifest, indent=2) + "\n")
    env["PS4_PKGTOOL"] = str(root / "build/pkgtool/PkgTool.Core")
    env["SFO_STYLE"] = "plain"
    env["DOLPHIN_PS4_MODULES_DIR"] = "/nonexistent"
    with (root / "evidence/package-build.log").open("w") as log:
        run(["bash", str(root / "refs/DolphinPS4/scripts/make-pkg.sh"), str(stage),
             "PSWK00010", "PSWaker Platform Diagnostic", args.app_version, "PSWAKERPROBE", str(output)],
            env=env, stdout=log, stderr=subprocess.STDOUT)
    packages = list(output.glob("*.pkg"))
    if len(packages) != 1:
        raise ValueError("Expected one diagnostic package")
    hashes = {"package": {"filename": packages[0].name, "sha256": digest(packages[0])},
              "eboot_sha256": digest(executable),
              "elf_sha256": digest(root / "build/probe/platform_diagnostic"),
              "build_id": identity(), "app_version": args.app_version}
    (root / "evidence/artifacts.json").write_text(json.dumps(hashes, indent=2) + "\n")
    shutil.copyfile(manifest_file, root / "evidence/build-info.json")
    print(json.dumps(hashes, indent=2))
