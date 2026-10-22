"""Summarize supplied console evidence; this does not launch or replay the diagnostic."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest_block(path, prefix):
    lines = path.read_text().splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    assert starts, f"Missing {prefix} in {path.name}"
    return lines[starts[-1]:], len(starts)


def fields(line):
    return dict(re.findall(r"([\w-]+)=([^ ;]+)", line))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Original output_logs directory (read only)")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    runs = []
    inventory = []
    for number in range(1, 4):
        source = args.input / f"pswaker-diagnostic-prototype 1.01 Run {number}"
        destination = here / f"run-{number}"
        destination.mkdir(exist_ok=True)
        for path in sorted(source.rglob("*")):
            if path.is_file():
                inventory.append({"path": path.relative_to(args.input).as_posix(),
                                  "bytes": path.stat().st_size, "sha256": sha256(path)})
        diagnostic, block_count = latest_block(source / "diagnostic.log", "BEGIN build=")
        # Embedded input manifests are already captured with the inspected 01.01 build.
        # Preserve current-run stage/results, never count the historical appended runs.
        diagnostic = [line for line in diagnostic if line and not line.startswith("MANIFEST")]
        (destination / "diagnostic-stages.log").write_text("\n".join(diagnostic) + "\n")
        runtime, runtime_count = latest_block(source / "runtime-preflight.log", "BEGIN runtime")
        (destination / "runtime-preflight.log").write_text("\n".join(runtime) + "\n")
        platform = [line for line in (source / "platform.log").read_text().splitlines()
                    if line.startswith(("[Aurora] Surface", "[Dawn] Display mode", "[Dawn] swapchain",
                                        "wsi/videoout:", "radv/ps4: device initialized"))]
        (destination / "platform-display.log").write_text("\n".join(platform) + "\n")
        failures = Counter(line.removeprefix("FAIL ") for line in diagnostic if line.startswith("FAIL "))
        end = fields(next(line for line in diagnostic if line.startswith("END ")))
        run = fields(next(line for line in diagnostic if line.startswith("RUN ")))
        resources = [fields(line) for line in diagnostic if line.startswith("RESOURCE ")]
        steady = [row for row in resources if float(row["seconds"]) >= 60]
        resource_ranges = {key: {"min": min(int(row[key]) for row in steady),
                                 "max": max(int(row[key]) for row in steady)}
                           for key in ("garlic", "onion", "buffers", "main-mspace-allocated", "flexible-available")}
        purple = sum(line == "PASS texture-depth-blend-offscreen-copy-readback" for line in diagnostic)
        state = int((source / "preflight-state.txt").read_text())
        assert diagnostic[0].startswith("BEGIN build=3a73181f6dfdb86ca4b4;")
        assert end["checks"] == "120" and end["failures"] == "241"
        assert failures == {"internal-render-size": 1, "Aurora-EFB-known-white-readback": 120,
                            "Aurora-offscreen-known-white-readback": 120}
        assert purple == 120 and state == number + 1 and run["launch"] == str(state)
        assert runtime[-1] == f"END failures=0 launch={state}; hardware gate remains incomplete"
        runs.append({"run": number, "diagnostic_begin_blocks_in_original": block_count,
                     "runtime_begin_blocks_in_original": runtime_count,
                     "identity": run, "preflight_state": state,
                     "resolution": next(line for line in diagnostic if line.startswith("RESOLUTION ")),
                     "end": end, "failures_by_check": failures, "purple_readbacks_passed": purple,
                     "controller_check_passed": "PASS controller-disconnect-reconnect-resume" in diagnostic,
                     "ten_minute_check_passed": "PASS ten-minute-loop" in diagnostic,
                     "resource_samples": len(resources), "resources_at_or_after_60_seconds": resource_ranges,
                     "last_resource": resources[-1],
                     "messages_after_end": diagnostic[diagnostic.index(next(line for line in diagnostic if line.startswith("END "))) + 1:]})
    (here / "retrieved-files.json").write_text(json.dumps(inventory, indent=2) + "\n")
    (here / "summary.json").write_text(json.dumps({"method": "Latest BEGIN block only; supplied evidence, no new console execution",
                                                "build": "3a73181f6dfdb86ca4b4", "runs": runs}, indent=2) + "\n")
    for run in runs:
        print(f"Run {run['run']}: launch={run['preflight_state']} checks=120 failures=241 purple=120/120; evidence captured")


if __name__ == "__main__":
    main()
