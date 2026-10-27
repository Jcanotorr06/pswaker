# Owner return: 01.11 cold and warm performance

The returned identity files, inspections and runtime manifests identify build
`5f4977765953663bf3f3`, complete package SHA-256
`b50cbdaf3e996faba3529a399891e397d3d1ff568a777ec628260762e1f8205c`.
The fixed 1280x720 allocation, stock textures and original 30 Hz logic remain.
This is diagnostic console evidence; no performance acceptance is claimed.

The owner confirmed retrieval **after normal port Quit**, **no video comparison**,
and **no Home/Quick Menu, suspend/resume, FTP or other interruption** between
warm Outset and forest sampling. Both returned launches lack recorder shutdown
and ordinary terminal Quit markers. That discrepancy remains an evidence gap;
it does not establish that the owner copied early or that shutdown failed.
Original owner JSONs retain the true timing flag and example verification text
byte-for-byte. Reviewed copies set `timing_method_verified=false` and record
the clarification. Physical timing verification remains pending.

## Independent results

Limits remain average >=29.5 FPS, p95 <=35 ms, p99 <=50 ms, maximum <=100 ms.
All recorded samples cover at least 120 seconds. Values below are calculated
from raw completed flips, without rounding shortfalls down to a pass.

| Launch / scene | Seconds | FPS | p95 ms | p99 ms | Max ms | Numerical result |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Cold Outset | 120.021615 | 28.761486 | 33.406414 | 66.736378 | 950.961669 | Average, p99 and maximum miss |
| Cold forest | 120.021617 | 30.002929 | 33.396649 | 33.425514 | 66.679737 | Meets numerical limits; timing/shutdown unverified |
| Warm Outset | 120.021621 | 29.977932 | 33.396985 | 33.434586 | 100.101750 | Maximum misses |
| Warm forest | — | — | — | — | — | No sample armed/exported after recorder became unavailable |

The owner's cold forest `p00` transcription is interpreted as p99 only because
the raw summary identifies that field. Warm Outset completed before the later
global timing error replaced the menu status with “Timing unavailable”. The raw
Outset sample remains, including its maximum shortfall. No forest measurements
are invented from surrounding frames. The original and reviewed analyses are
retained separately. Legacy CSVs lack a simultaneous kernel clock read, so the
new analyzer deliberately retains their original conservative invalid verdict.

## Findings and bounded correction

Cold Outset has 6,237.287177 ms of recorded shader waits, including 81 waits
over 35 ms and 63 shader-correlated presentation hitches. The 950.961669 ms
interval contains 940.284334 ms across ten shader waits. Cold shader stalls
remain unresolved; preparation does not excuse these gameplay freezes.
Warm Outset has one 59.981430 ms shader wait; its 100.101750 ms maximum has no
shader wait attributed to that interval. See [diagnosis.json](diagnosis.json).

Median heartbeat diagnostic cost is 1.622510 ms cold and 1.594331 ms warm,
consistent with improvement after removing the duplicate debugger sink. This
is an observed operation duration, not an isolated syscall benchmark. Cold
input diagnostics still reach 117.424155 ms, and a recorder flush reaches
160.558390 ms. The old recorder performs CSV writes, flushes and fsyncs under
the same mutex as frame capture/submission. A deterministic external blocked
flush reproduces the resulting submission/observation stall. The follow-up
moves that I/O to a bounded writer, retaining invalid evidence on write/queue
failure and draining it at normal shutdown. Other OS/native-log stalls remain
possible; their isolated causes are not established by these captures.

At warm monotonic time `738397893602870`, about 59 seconds after Outset ended,
the recorder emits `unverified-flip-clock-domain` for a port/UI completion.
Flip count/argument 7863 is consecutive, its timestamp is monotonic, and its
observation offset is about 159.37 ms above the launch baseline. The next
completion returns to about 0.51 ms. The old 100 ms age check treats delayed
observation as permanent clock-domain failure and blocks any subsequent arm.
An exported-record regression reproduces exactly that later-forest loss.
The new recorder records the delay, retains the completion and permits later
sampling. New raw `read_tsc` fields independently calibrate kernel reads against
monotonic observations; missing completions and genuine clock errors remain
invalid. The source of the underlying scheduling delay is not established.

[original-file-inventory.json](original-file-inventory.json) inventories supplied
originals by size/SHA-256. Raw launch files, original owner reports, ordinary
logs and original analyses are retained. Reviewed analyses return exit 2.
No quality/threshold change or substitute evidence is approved. Use the new
candidate's exact identity for renewed measurements; issue #22 remains open
and final integrated acceptance remains #23.
