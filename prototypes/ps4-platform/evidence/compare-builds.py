#!/usr/bin/env python3
"""Inspect two finished clean builds; this does not run PS4 code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def elf_sections(path, root):
    data = path.read_bytes()
    assert data[:6] == b"\x7fELF\x02\x01", "Expected little-endian ELF64"
    assert struct.unpack_from("<H", data, 18)[0] == 62, "Expected x86-64"
    phoff, shoff = struct.unpack_from("<QQ", data, 32)
    phsize, phnum, shsize, shnum, names_index = struct.unpack_from("<HHHHH", data, 54)
    loads = [struct.unpack_from("<IIQQQQQQ", data, phoff + i * phsize) for i in range(phnum)]
    loads = [item for item in loads if item[0] == 1]
    assert loads and loads[0][3] == 0, "First PT_LOAD must start at zero"
    sections = [struct.unpack_from("<IIQQQQIIQQ", data, shoff + i * shsize) for i in range(shnum)]
    names = data[sections[names_index][4]:][:sections[names_index][5]]
    result = {}
    for header in sections:
        if not header[2] & 2:
            continue
        name = names[header[0]:].split(b"\0", 1)[0].decode()
        content = data[header[4]:][:header[5]] if header[1] != 8 else b""
        normalized = content.replace(str(root).encode(), b"/tmp/pswaker-clean-x")
        result[name] = {"size": header[5], "sha256": hashlib.sha256(content).hexdigest(),
                        "normalized_sha256": hashlib.sha256(normalized).hexdigest(), "type": header[1]}
    return result


def inspect(root):
    artifact = json.loads((root / "evidence/artifacts.json").read_text())
    package = root / "out" / artifact["package"]["filename"]
    assert sha(package) == artifact["package"]["sha256"]
    extracted = root / "evidence/package-extract"
    if not extracted.exists():
        extracted.mkdir()
        with (root / "evidence/package-extract.log").open("w") as log:
            subprocess.run([str(root / "build/pkgtool/PkgTool.Core"), "pkg_extract", str(package), str(extracted)],
                check=True, env=dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="1"), stdout=log, stderr=subprocess.STDOUT)
    payload = extracted / "uroot"
    files = {path.relative_to(payload).as_posix(): sha(path) for path in sorted(payload.rglob("*")) if path.is_file()}
    tool = str(root / "build/pkgtool/PkgTool.Core")
    entries = subprocess.check_output([tool, "pkg_listentries", str(package)], text=True)
    (root / "evidence/package-entries.txt").write_text(entries)
    metadata = extracted / "metadata"
    metadata.mkdir(exist_ok=True)
    for entry_name, filename in (("PARAM_SFO", "param.sfo"), ("ICON0_PNG", "icon0.png")):
        row = next(line for line in entries.splitlines() if line.split() and line.split()[-1] == entry_name)
        index = row.split()[3]
        subprocess.run([tool, "pkg_extractentry", str(package), index, str(metadata / filename)], check=True)
        files["sce_sys/" + filename] = sha(metadata / filename)
    assert files.get("eboot.bin") == artifact["eboot_sha256"], "Package eboot differs from checked SELF"
    manifest = json.loads((payload / "build-info.json").read_text())
    assert manifest["diagnostic_build_id"] == artifact["build_id"]
    assert manifest["eboot_sha256"] == artifact["eboot_sha256"]
    elf = root / "build/probe/platform_diagnostic"
    assert sha(elf) == artifact["elf_sha256"]
    assert artifact["build_id"].encode() in elf.read_bytes(), "Compiled build identity missing"
    for path in files:
        assert not path.lower().endswith((".iso", ".rvz", ".dol", ".gcm", ".gci", ".key")), "Unexpected game/key payload"
    expected = {"eboot.bin", "build-info.json", "sce_sys/icon0.png", "sce_sys/param.sfo",
                "sce_sys/about/right.sprx", "sce_module/libSceFios2.prx", "sce_module/libc.prx", "sce_sys/keystone"}
    assert set(files) == expected, "Unexpected packaged file inventory: " + str(set(files) ^ expected)
    sfo = (metadata / "param.sfo").read_bytes()
    assert sfo[:4] == b"\0PSF", "Expected SFO metadata"
    key_start, data_start, count = struct.unpack_from("<III", sfo, 8)
    fields = {}
    for i in range(count):
        key_offset, kind, length, maximum, offset = struct.unpack_from("<HHIII", sfo, 20 + i*16)
        key = sfo[key_start + key_offset:].split(b"\0",1)[0].decode()
        value = sfo[data_start+offset:][:length]
        fields[key] = int.from_bytes(value,"little") if kind == 0x0404 else value.rstrip(b"\0").decode()
    assert fields["TITLE_ID"] == "PSWK00010" and fields["APP_VER"] == artifact.get("app_version", "01.00")
    assert fields["TITLE"] == "PSWaker Platform Diagnostic" and fields["CATEGORY"] == "gd"
    return {"artifacts": artifact, "elf_sections": elf_sections(elf, root), "package_files": files,
            "package_sfo": fields,
            "source_archives": manifest["sources"], "sdk": manifest["sdk"],
            "local_adaptations": manifest["local_adaptations"],
            "input_closure": manifest["input_closure"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    first, second = inspect(args.first.resolve()), inspect(args.second.resolve())
    assert first["artifacts"]["build_id"] == second["artifacts"]["build_id"], "Different diagnostic source/host identity"
    for item in ("source_archives", "sdk", "local_adaptations"):
        assert first[item] == second[item], "Different locked inputs: " + item
    for item in ("mesa_revision", "libdrm_revision", "host_versions", "host_packages", "dawn_deps", "sdk_package_metadata", "nuget_locks"):
        assert first["input_closure"][item] == second["input_closure"][item], "Different input closure: " + item
    first_downloads = json.dumps(first["input_closure"]["cmake_downloads"], sort_keys=True).replace(str(args.first.resolve()), "/tmp/pswaker-clean-x")
    second_downloads = json.dumps(second["input_closure"]["cmake_downloads"], sort_keys=True).replace(str(args.second.resolve()), "/tmp/pswaker-clean-x")
    # urlinfo file hashes include the source directory itself, so compare their normalized text;
    # downloaded archive hashes must still match exactly.
    def archive_closure(value):
        return [{key: field for key, field in item.items() if key != "sha256" or "text" not in item} for item in json.loads(value)]
    assert archive_closure(first_downloads) == archive_closure(second_downloads), "Different CMake source closure"
    differences = {}
    for name in sorted(first["elf_sections"].keys() | second["elf_sections"].keys()):
        a, b = first["elf_sections"].get(name), second["elf_sections"].get(name)
        if a != b:
            differences[name] = {"first": a, "second": b,
                "equal_after_normalizing_build_root": bool(a and b and a["normalized_sha256"] == b["normalized_sha256"])}
    files_differing = [name for name, value in first["package_files"].items() if second["package_files"].get(name) != value]
    report = {"scope": "Two clean build directories on the recorded Ubuntu/WSL2 host; no PS4 execution",
              "first": first, "second": second, "allocated_elf_section_differences": differences,
              "packaged_files_differing": files_differing,
              "byte_identical_elf": first["artifacts"]["elf_sha256"] == second["artifacts"]["elf_sha256"],
              "byte_identical_pkg": first["artifacts"]["package"]["sha256"] == second["artifacts"]["package"]["sha256"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("scope", "allocated_elf_section_differences", "packaged_files_differing", "byte_identical_elf", "byte_identical_pkg")}, indent=2))
