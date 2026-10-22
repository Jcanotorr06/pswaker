"""Capture supplied 01.02 evidence. This parses logs; it never runs PS4 code."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil

BUILD = "4b1830b0443ff170425e"
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fields(line):
    return dict(re.findall(r"([\w-]+)=([^ ;]+)", line))


def latest(path, prefix):
    lines = path.read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    assert starts, f"Missing {prefix} in {path}"
    return lines[starts[-1]:], len(starts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Owner's output directory, read only")
    args = parser.parse_args()
    inventory = [{"path": p.relative_to(args.input).as_posix(), "bytes": p.stat().st_size,
                  "sha256": digest(p)} for p in sorted(args.input.rglob("*")) if p.is_file()]
    runs = []
    for number, label in enumerate(("cold", "warm 1", "warm 2"), 1):
        source = args.input / f"01.02 {label}"
        destination = HERE / f"run-{number}"
        destination.mkdir(exist_ok=True)
        block, count = latest(source / "diagnostic.log", "BEGIN build=")
        # The app uses fgets(1024): a long JSON string is split across MANIFEST
        # chunks. Concatenate chunks, without introducing newlines inside strings.
        manifest = json.loads("".join(line.removeprefix("MANIFEST ") for line in block
                                         if line.startswith("MANIFEST ")))
        recorded_manifest = json.loads((HERE.parent / "aurora-correction-20261022/native/build-info.json").read_text())
        assert manifest == recorded_manifest, "Console embedded manifest differs from inspected 01.02"
        diagnostic = [line for line in block if line and not line.startswith("MANIFEST")]
        runtime, runtime_count = latest(source / "runtime-preflight.log", "BEGIN runtime")
        state = int((source / "preflight-state.txt").read_text())
        run = fields(next(line for line in diagnostic if line.startswith("RUN ")))
        end = fields(next(line for line in diagnostic if line.startswith("END ")))
        failures = Counter(line.removeprefix("FAIL ") for line in diagnostic if line.startswith("FAIL "))
        passes = Counter(line.removeprefix("PASS ") for line in diagnostic if line.startswith("PASS "))
        resources = [fields(line) for line in diagnostic if line.startswith("RESOURCE ")]
        steady = [row for row in resources if float(row["seconds"]) >= 60]
        ranges = {key: {"min": min(int(row[key]) for row in steady),
                        "max": max(int(row[key]) for row in steady),
                        "first": int(steady[0][key]), "last": int(steady[-1][key])}
                  for key in ("garlic", "onion", "buffers", "main-mspace-allocated", "flexible-available")}
        assert diagnostic[0].startswith(f"BEGIN build={BUILD};")
        assert end["failures"] == "0" and not failures and end["checks"] == "120"
        assert state == number + 6 and run["launch"] == str(state)
        assert run["cache-entries-before-Aurora"] == ("0" if number == 1 else "2")
        assert runtime[-1] == f"END failures=0 launch={state}; hardware gate remains incomplete"
        assert not any(line.startswith("FAIL ") for line in runtime)
        for check in ("Aurora-EFB-known-white-readback", "Aurora-offscreen-known-white-readback",
                      "texture-depth-blend-offscreen-copy-readback", "allocated-EFB-render-size"):
            assert passes[check] == 120, (label, check, passes[check])
        for check in ("internal-render-size", "GX-pipeline-preparation", "controller-disconnect-reconnect-resume",
                      "ten-minute-loop", "GPU-queue-drained", "synthetic-audio-API-errors"):
            assert passes[check] == 1, (label, check)
        pixels = [line for line in diagnostic if line.startswith("PIXEL ")]
        assert len(pixels) == 240
        assert all("first=255,255,255,255 expected=255,255,255,255 mismatches=0/1024" in line for line in pixels)
        assert sum(line == "TARGET EFB=1280x720 format=22" for line in diagnostic) == 120
        recreations = diagnostic.count("STAGE create-targets-and-textured-depth-blend-pipelines")
        assert recreations == 10, "Initial targets plus nine in-loop recreations expected"
        assert len(resources) == 21 and float(resources[-1]["seconds"]) >= 600
        assert all(row["audio-errors"] == "0" for row in resources)
        shutdown = diagnostic.index("STAGE shutdown")
        warnings = [line for line in diagnostic if line.startswith("AURORA level=2")]
        assert not any(line.startswith("AURORA level=2") for line in diagnostic[:shutdown])
        assert not any("mapping Aborted" in line for line in diagnostic)
        assert diagnostic.index("PASS GPU-queue-drained") < diagnostic.index("STAGE Aurora-shutdown-begin")
        assert diagnostic.index("STAGE Aurora-shutdown-begin") < diagnostic.index("AURORA level=2 module=aurora::gpu Device lost: Device was destroyed.") < diagnostic.index("STAGE Aurora-shutdown-complete")
        assert diagnostic[-1].startswith("END ")
        platform = (source / "platform.log").read_text().splitlines()
        assert "exit status 0: asking the shell to close the title" in platform
        display = [line for line in platform if line.startswith(("[Aurora] Surface", "[Dawn] Display mode", "[Dawn] swapchain", "wsi/videoout:", "radv/ps4: device initialized"))]
        for filename, lines in (("diagnostic-stages.log", diagnostic), ("runtime-preflight.log", runtime), ("platform-display.log", display)):
            (destination / filename).write_text("\n".join(lines) + "\n")
        shutil.copyfile(source / "preflight-state.txt", destination / "preflight-state.txt")
        result = {"run": number, "owner_cache_label": label,
                  "diagnostic_begin_blocks_in_original": count, "runtime_begin_blocks_in_original": runtime_count,
                  "embedded_manifest_matches_inspected_candidate": True, "identity": run, "preflight_state": state,
                  "resolution": next(line for line in diagnostic if line.startswith("RESOLUTION ")),
                  "preparation": next(line for line in diagnostic if line.startswith("PREPARATION ")),
                  "end": end, "failure_lines": failures, "passes_by_check": passes,
                  "target_creations_including_initial": recreations,
                  "pad_transitions": [line for line in diagnostic if line.startswith("PAD ")],
                  "resource_samples": len(resources), "resources_at_or_after_60_seconds": ranges,
                  "first_resource": resources[0], "last_resource": resources[-1],
                  "shutdown_warnings": warnings, "mapping_aborted": False,
                  "platform_exit_status": 0}
        runs.append(result)
        print(f"{label}: build={BUILD} launch={state} cache={run['cache-entries-before-Aurora']} frames={end['frames']} checks=120 failures=0; 240 white + 120 purple comparisons pass")
    shutil.copyfile(args.input / "visual.jpg", HERE / "visual.jpg")
    (HERE / "retrieved-files.json").write_text(json.dumps(inventory, indent=2) + "\n")
    (HERE / "summary.json").write_text(json.dumps({"method": "Latest BEGIN block per supplied snapshot; parser is not console execution", "build": BUILD, "runs": runs}, indent=2) + "\n")


if __name__ == "__main__":
    main()
