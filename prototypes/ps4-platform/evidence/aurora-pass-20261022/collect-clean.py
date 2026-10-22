"""Inspect/capture a newly compiled pair. This never certifies PS4 execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
PLATFORM = HERE.parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--evidence-base-revision", required=True,
                        help="Full verified base revision; Windows worktree Git pointers are not Linux paths")
    args = parser.parse_args()
    assert re.fullmatch(r"[0-9a-f]{40}", args.evidence_base_revision)
    roots = [args.first.resolve(), args.second.resolve()]
    build_id = "4b1830b0443ff170425e"
    candidate = json.loads((args.candidate / "evidence/build-info.json").read_text())
    assert candidate["diagnostic_build_id"] == build_id
    candidate_hashes = json.loads((args.candidate / "evidence/artifacts.json").read_text())
    assert candidate_hashes["package"]["sha256"] == "9764e1acb1e7fa8a17c8c7aee9ca3793ac908da38368188b52de33a49dd399be"
    spec = importlib.util.spec_from_file_location("compare", PLATFORM / "evidence/compare-builds.py")
    compare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compare)
    inspections = []
    for name, root in zip(("clean-a", "clean-b"), roots):
        log = (root / "evidence/clean-build.log").read_text()
        assert "COMPLETE host-build-only" in log
        assert "STAGE fresh-download-cache" in log
        inspection = compare.inspect(root)
        assert inspection["artifacts"]["build_id"] == build_id
        assert inspection["artifacts"]["app_version"] == "01.02"
        for key in ("source_archives", "sdk", "local_adaptations"):
            candidate_key = "sources" if key == "source_archives" else key
            assert inspection[key] == candidate[candidate_key], key
        for key in ("mesa_revision", "libdrm_revision", "host_versions", "host_packages", "dawn_deps", "sdk_package_metadata", "nuget_locks"):
            assert inspection["input_closure"][key] == candidate["input_closure"][key], key
        def downloads(value, base):
            rows = json.loads(json.dumps(value).replace(str(base), "/tmp/pswaker-clean-x"))
            # urlinfo text includes its build root. The downloaded archive
            # digest still compares exactly; only the urlinfo's own hash is omitted.
            return [{key: field for key, field in item.items()
                     if key != "sha256" or "text" not in item} for item in rows]
        assert downloads(inspection["input_closure"]["cmake_downloads"], root) == downloads(candidate["input_closure"]["cmake_downloads"], args.candidate.resolve()), "Candidate CMake source closure differs"
        elf = (root / "build/probe/platform_diagnostic").read_bytes()
        for marker in (b"GX-initialize-alpha-framebuffer-and-VI-scale", b"allocated-EFB-render-size",
                       b"prepare-GX-pipelines-before-known-result-checks", b"GPU-queue-drained", b"Aurora-shutdown-complete"):
            assert marker in elf, marker
        destination = HERE / name
        destination.mkdir(exist_ok=True)
        # Keep logs/manifests only. Packages, SDK archives, extracted payload and
        # target archives stay in the local build roots.
        for path in sorted((root / "evidence").iterdir()):
            if path.is_file() and path.suffix in {".log", ".json", ".txt", ".sha256"}:
                shutil.copyfile(path, destination / path.name)
        inspections.append(inspection)
    subprocess.run(["python3", str(PLATFORM / "evidence/compare-builds.py"),
                    *map(str, roots), str(HERE / "comparison.json")], check=True,
                   stdout=(HERE / "comparison.log").open("w"), stderr=subprocess.STDOUT)
    subprocess.run(["python3", str(PLATFORM / "evidence/explain-differences.py"),
                    "--first", str(roots[0]), "--second", str(roots[1]),
                    "--output", str(HERE / "difference-analysis.json")], check=True,
                   stdout=(HERE / "difference-analysis.log").open("w"), stderr=subprocess.STDOUT)
    comparison = json.loads((HERE / "comparison.json").read_text())
    assert set(comparison["allocated_elf_section_differences"]) <= {".text", ".rodata", ".rela.dyn"}
    differences = json.loads((HERE / "difference-analysis.json").read_text())
    assert differences["instruction_comparison"]["other_differing_instructions_count"] == 0
    assert differences["relocation_comparison"]["other_than_equal_nul_terminated_rodata_targets"] == 0
    summary = {"scope": "Two new absent build roots; freshly compiled target dependencies, Aurora, probe and packager; no console execution",
               "diagnostic_source_revision": "b45d5e29246bd1c86d78f9ca165cbc3f7b4d6e5b",
               "evidence_base_revision": args.evidence_base_revision,
               "build_id": build_id,
               "console_candidate_matches_source_sdk_adaptations_host_and_dependency_pins": True,
               "roots": list(map(str, roots)),
               "artifacts": [inspection["artifacts"] for inspection in inspections],
               "captured_evidence_sha256": {str(p.relative_to(HERE)): digest(p)
                   for folder in ("clean-a", "clean-b") for p in sorted((HERE / folder).rglob("*")) if p.is_file()}}
    (HERE / "clean-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({key: summary[key] for key in ("scope", "build_id", "artifacts")}, indent=2))


if __name__ == "__main__":
    main()
