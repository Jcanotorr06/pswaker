"""Preserve host reproduction/build/package evidence, without console claims."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

here = Path(__file__).resolve().parent
root, host = (Path(value).resolve() for value in sys.argv[1:])
def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

for kind, base, names in (
    ('host-repro', host, ['differential-check.log', 'baseline.log', 'repeat.log', 'drain.log',
                        'scale.log', 'initialize-repeat.log', 'alpha.log', 'corrected.log',
                        'dawn-configure.log', 'dawn-build.log', 'sdl-configure.log', 'sdl-build.log',
                        'repro-configure.log', 'repro-build.log']),
    ('native', root / 'evidence', ['artifacts.json', 'build-info.json', 'input-closure.json',
                                  'source-archives.json', 'local-adaptations.json',
                                  'aurora-retry-inspection.json', 'aurora-candidate-build.log',
                                  'aurora-atomic-compile-failure.log', 'probe-configure.log',
                                  'probe-build.log', 'pkgtool-build.log', 'package-build.log',
                                  'package-extract.log', 'package-entries.txt']),
):
    destination = here / kind
    destination.mkdir(exist_ok=True)
    for name in names:
        shutil.copyfile(base / name, destination / name)

baseline = json.loads((root / 'aurora-baseline-01.01/evidence/retry-inspection.json').read_text())
candidate = json.loads((root / 'evidence/aurora-retry-inspection.json').read_text())
for key in ('source_archives', 'sdk', 'local_adaptations', 'cached_runtime_archives'):
    assert baseline[key] == candidate[key], key
for key in ('mesa_revision', 'libdrm_revision', 'dawn_deps', 'sdk_package_metadata'):
    assert baseline['input_closure'][key] == candidate['input_closure'][key], key
headers = {}
for name in ('webgpu.h', 'webgpu_cpp.h', 'dawn_proc_table.h'):
    native_header = root / 'build/dawn/gen/include/dawn' / name
    host_header = host / 'dawn/gen/include/dawn' / name
    assert digest(native_header) == digest(host_header), name
    headers[name] = digest(host_header)
summary = {
    'scope': 'Local Aurora reproduction and one incremental PS4 candidate; no 01.02 console evidence',
    'candidate_source_revision': 'b45d5e29246bd1c86d78f9ca165cbc3f7b4d6e5b',
    'unchanged_selected_platform_and_runtime': True,
    'identical_host_native_generated_API_headers': headers,
    'host_repro_executable_sha256': digest(host / 'repro/aurora-repro'),
    'artifacts': candidate['artifacts'],
    'new_clean_build_pair': False,
    'evidence_sha256': {
        str(p.relative_to(here)): digest(p)
        for folder in ('host-repro', 'native') for p in sorted((here / folder).rglob('*')) if p.is_file()
    },
}
(here / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({key: summary[key] for key in ('scope', 'unchanged_selected_platform_and_runtime', 'artifacts')}, indent=2))
