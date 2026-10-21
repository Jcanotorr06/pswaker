"""Record the supplied owner report; do not pretend to operate the console."""
from pathlib import Path
import subprocess

here = Path(__file__).resolve().parent
answers = [
    '97fc99208640c483fdc2',
    'Previously confirmed PS4 Slim / 9.00 / GoldHEN v2.4b18; not reconfirmed in this message',
    'crash', 'ce-34878-0', 'about 10', 'black', 'silent',
    'diagnostic.log, runtime-preflight.log, platform.log, preflight-state.txt',
    'aurora-initialize; Error initializing SDL: No available video device; Error initializing window',
]
command = ['bash', str(here.parent.parent/'startup-probe/retry.sh'), 'full', str(here/'owner'), '--record-existing']
result = subprocess.run(command, input='\n'.join(answers)+'\n', text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(here/'owner/observation-capture.log').write_text(result.stdout)
assert result.returncode == 20, result.stdout
print(result.stdout)
