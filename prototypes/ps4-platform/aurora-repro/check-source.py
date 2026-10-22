"""Verify the preserved draw really is the failed diagnostic's draw function."""
from pathlib import Path
import hashlib
import subprocess

here = Path(__file__).resolve().parent
revision = "605d57a581e3657ce4a485140f17552b1c6119d2"
# The existing worktree was created by Windows Git; use its ancestor's object
# database explicitly when running this read-only check from WSL.
git_dir = next((p / ".git" for p in here.parents if (p / ".git").is_dir()), None)
git = ["git", f"--git-dir={git_dir}"] if git_dir else ["git"]
source = subprocess.check_output(
    [*git, "show", f"{revision}:prototypes/ps4-platform/probe/main.cpp"],
    cwd=here, text=True,
)
start = source.index("void triangle(")
end = source.index("\n}\nint main", start)
expected = source[start:end].strip()
actual = (here / "baseline-scene.hpp").read_text().split("\n", 1)[1].strip()
assert actual == expected, "Preserved draw differs from failed diagnostic"
shared = (here.parent / "probe/gx-scene.hpp").read_text().split("\n", 1)[1].strip()
assert shared == expected, "Shared draw changed; review the baseline comparison"
print("PASS preserved-baseline-scene", revision, hashlib.sha256(expected.encode()).hexdigest())
