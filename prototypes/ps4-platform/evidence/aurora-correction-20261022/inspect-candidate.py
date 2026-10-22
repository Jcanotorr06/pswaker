"""Inspect 01.02's exact package payload and compiled Aurora checkpoints."""
import importlib.util
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
root = Path(sys.argv[1]).resolve()
assert (root / 'evidence').is_dir() and (root / 'build/probe').is_dir()
# The shared inspector must extract this binary, not reuse 01.01's extraction.
old = root / 'evidence/package-extract'
if old.exists():
    saved = root / 'evidence/package-extract-before-01.02'
    assert not saved.exists(), 'Preserve the existing extraction explicitly before inspecting again'
    old.rename(saved)
spec = importlib.util.spec_from_file_location('build_comparison', here.parent / 'compare-builds.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
record = module.inspect(root)
assert record['artifacts']['app_version'] == '01.02'
assert record['package_sfo']['APP_VER'] == '01.02'
binary = (root / 'build/probe/platform_diagnostic').read_bytes()
for marker in (b'GX-initialize-alpha-framebuffer-and-VI-scale', b'allocated-EFB-render-size',
               b'GX-pipeline-preparation', b'GPU-queue-drained', b'Aurora-shutdown-complete',
               b'expected=255,255,255,255', b'completion=%d (0=timeout,-1=map-failure)'):
    assert marker in binary, marker
record['cached_runtime_archives'] = {p.name: module.sha(p) for p in sorted((root / 'sysroot/lib').glob('*.a'))}
(root / 'evidence/aurora-retry-inspection.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'artifact': record['artifacts'], 'sfo_version': record['package_sfo']['APP_VER'],
                  'package_files': sorted(record['package_files']),
                  'scope': 'Host package inspection; PS4 01.02 not run.'}, indent=2))
