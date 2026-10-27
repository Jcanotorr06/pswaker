#!/usr/bin/env python3
"""Small, explicit diagnostic adaptations; emits the ordered patch evidence."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path


def adapt(root, relative, edits):
    path = root / relative
    before = path.read_text()
    after = before
    for old, new in edits:
        if new in after:
            continue
        if after.count(old) != 1:
            raise ValueError("Unexpected pinned source context: " + relative)
        after = after.replace(old, new)
    folder = root / "evidence/local-patches"
    folder.mkdir(parents=True, exist_ok=True)
    patchfile = folder / (relative.replace("/", "-") + ".patch")
    if after != before:
        patchfile.write_text("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                              fromfile="a/" + relative, tofile="b/" + relative)))
        path.write_text(after)
    if patchfile.exists():
        return {"path": relative, "patch": patchfile.name,
                "patch_sha256": hashlib.sha256(patchfile.read_bytes()).hexdigest(),
                "prepared_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    root = parser.parse_args().root.resolve()
    records = []
    records.append(adapt(root, "refs/DolphinPS4/toolchain/env.sh", [
        ("-fPIC -funwind-tables \\\n", "-fPIC -funwind-tables -march=btver2 -ftls-model=initial-exec \\\n")]))
    records.append(adapt(root, "refs/DolphinPS4/port/ps4_dlmalloc.c", [
        ("#define NO_MALLINFO 1", "#define NO_MALLINFO 0"),
        ("/* Integrity check for diagnostics:", "/* Diagnostic main-mspace allocated bytes (includes reserved thread arenas). */\nsize_t pswaker_mspace_used(void* msp) { return mspace_mallinfo(msp).uordblks; }\n\n/* Integrity check for diagnostics:")]))
    records.append(adapt(root, "refs/DolphinPS4/port/ps4_runtime.cpp", [
        ("}  // extern \"C\"", "}  // extern \"C\"\n\nextern \"C\" size_t pswaker_mspace_used(void*);\nextern \"C\" size_t pswaker_heap_used(void) { return pswaker_mspace_used(getHeap()); }")]))
    records.append(adapt(root, "src/native-platform/ps4/native/platform.c", [
        ("if (scePadReadState(state->handle, &sample) < 0 || !sample.connected)\n         continue;",
         "if (scePadReadState(state->handle, &sample) < 0 || !sample.connected) {\n         const int32_t user = state->user, handle = state->handle;\n         pad_rest(state);\n         state->user = user;\n         state->handle = handle;\n         continue;\n      }")]))
    records.append(adapt(root, "refs/DolphinPS4/scripts/make-pkg.sh", [
        ('"$TOOLS/PkgTool.Core" sfo_new', '"${PS4_PKGTOOL:-$TOOLS/PkgTool.Core}" sfo_new'),
        ('"$TOOLS/PkgTool.Core" sfo_setentry', '"${PS4_PKGTOOL:-$TOOLS/PkgTool.Core}" sfo_setentry'),
        ('"$TOOLS/PkgTool.Core" pkg_build', '"${PS4_PKGTOOL:-$TOOLS/PkgTool.Core}" pkg_build')]))
    (root / "evidence/local-adaptations.json").write_text(json.dumps(records, indent=2) + "\n")
    print("Recorded diagnostic CPU/TLS, memory measurement and neutral-input adaptations.")
