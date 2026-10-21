"""Cross-check supplied build identity and original packaged dependency evidence."""
import hashlib
import json
from pathlib import Path
import subprocess

here = Path(__file__).resolve().parent
# The prototype is in an isolated worktree; the owner's artifact directory is at
# the original checkout, not inside that worktree.
baseline = Path('/mnt/c/Users/Joseph Cano/Code/pswaker/local-research/diagnostic-artifacts')
artifact = json.loads((baseline/'artifacts.json').read_text())
assert artifact['build_id'] == '97fc99208640c483fdc2'
elf = baseline/'platform_diagnostic'
assert hashlib.file_digest(elf.open('rb'),'sha256').hexdigest() == artifact['elf_sha256']
symbols = subprocess.check_output(['llvm-nm-21','--defined-only',str(elf)],text=True,stderr=subprocess.DEVNULL)
drivers = [line for line in symbols.splitlines() if line.split()[-1] in ('DUMMY_bootstrap','OFFSCREEN_bootstrap')]
assert len(drivers) == 2, drivers
output = {'baseline_build_id':artifact['build_id'],'verified_elf_sha256':artifact['elf_sha256'],
          'compiled_video_bootstraps':drivers,
          'console_log_identifies_same_build':artifact['build_id'] in (here/'owner/diagnostic-stages.log').read_text(),
          'limit':'Host inspection of the original local ELF and supplied logs; not console execution.'}
(here/'baseline-inspection.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(output,indent=2))
