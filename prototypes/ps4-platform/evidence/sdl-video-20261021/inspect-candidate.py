"""Inspect the built retry package with the existing package/ELF checks."""
import importlib.util
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location('build_comparison', here.parent/'compare-builds.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
record = module.inspect(root)
record['cached_runtime_archives'] = {p.name: module.sha(p) for p in sorted((root/'sysroot/lib').glob('*.a'))}
assert record['artifacts']['app_version'] == '01.01'
assert record['package_sfo']['APP_VER'] == '01.01'
binary = (root/'build/probe/platform_diagnostic').read_bytes()
assert b'SDL-dummy-video-selected' in binary and b'SDL_VIDEO active=%s' in binary
(root/'evidence/retry-inspection.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'artifact':record['artifacts'], 'sfo_version':record['package_sfo']['APP_VER'],
                  'package_files':sorted(record['package_files']),
                  'compiled_SDL_configuration_checkpoints':True,
                  'scope':'Host artifact inspection only; PS4 retry pending.'},indent=2))
