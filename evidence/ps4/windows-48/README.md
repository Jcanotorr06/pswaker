# Clean Windows acceptance handoff (#48)

Status on **2026-10-27: awaiting human execution**. No clean-system acceptance
run is claimed. Follow the [owner checklist](../../../docs/desktop/Clean-windows-checklist.md)
and fill a private copy of the [result template](../../../docs/desktop/Clean-windows-results.example.md)
for each supported OS. Keep issue [#48](https://github.com/Jcanotorr06/pswaker/issues/48)
open and `ready-for-human` until the actual returned evidence passes review.

## Acceptance matrix

| Required observation | Clean Windows 10 x64 | Clean Windows 11 x64 |
| --- | --- | --- |
| Ordinary standard account; no developer prerequisites | pending | pending |
| Network disabled before install through uninstall | pending | pending |
| Exact production installer A / first launch / owner-image package | pending | pending |
| Readable selection/version/progress/result/manual instructions | pending | pending |
| Fresh actual-output inspection and exact artifact identities | pending | pending |
| Rejection, access/space/collision, packaging/inspection failure | pending | pending |
| Cancellation/interruption, cleanup and fresh retry; owner data preserved | pending | pending |
| Useful explicit private diagnostics and redaction review | pending | pending |
| Manual installer B update, verified package and stable console IDs | pending | pending |
| Uninstall preserves owner images and complete packages | pending | pending |
| Measured Windows validation/assembly/verification timings | pending | pending |

## Available private reference candidates

The retained #46 pair can be used for this matrix if delivered privately with
their matching audits. Rehash on delivery; a filename or this table is not enough.
If using replacement candidates, record their new identities and repeat the
matrix. Desktop A/B carry the same native program, so this pair exercises a
desktop update, not a native program update or console save/settings migration.

| Candidate | Installer SHA-256 | Installed application-release.json SHA-256 |
| --- | --- | --- |
| A: 0.46.0.0 | `4a56838bff28e6f014b2dd4b05aa07453110631d80e6a20168dc8a195cb7f68d` | `187a44c074766f1e27a7edd2c0b5a9569874109f6b159ef866947c8a99836642` |
| B: 0.46.1.0 | `8eec0002d4007ec044acf0c449677c1565249e7ff6e68c5d2a5da14de4b0a086` | `8f029a87b22316be8b877cf6cf6282bead5d99a73502fdf63ba8f2582f738a0b` |

Both bundle program **01.13**, compiled build `f236a035ac406940e76a`, SELF SHA-256
`a95ea92a37b5d080937cba386f0f0cb43a8e450999cbafb4da5c7861ac5e624e`, matching
ELF SHA-256 `a99bcca89c4c0a54d808400ddffbfdca6d8df620d601b814386bf2fcd38e9ebb`,
and LibOrbisPkg revision `594021fdc435409f755a6ae0781b65ec6cec846c` with bundled
runtime built by SDK **8.0.427**. Audit manifests retain the remaining file
inventories. The stable console identity is `PSWK00001` /
`IV0000-PSWK00001_00-PSWAKERGAME00000`.

The existing [#42 development-host observations](../windows-42/README.md),
[#43 controlled failure checks](../windows-43/README.md) and
[#46 installed lifecycle](../windows-46/README.md) are prior evidence only. The
#46 run used Windows 11 build 26200, a filtered administrator account and no
physical network isolation. It does not fill any clean-system matrix cell.
Automated synthetic fixtures do not establish production-image acceptance.

## Private handoff preparation

Both retained installer files were rehashed against their matching audit records
and copied with those audits into an ignored local handoff folder. The folder
also contains this checklist, two blank OS records, a verified supported-image
copy and five labelled negative copies. The unchanged production validator
rejected all five: region header, revision header, invalid container magic,
truncated size and modified required DOL content. The original image's before/
after SHA-256 matched
`ec2d4ee790f48bee3d4c10feed166370df895f474e8db3f9af3b16ee001436df`.
Exact fixture mutations and hashes remain in the private preparation record.
Nothing from that folder is committed or uploaded. These are maintainer
preparation observations, not installed-app or clean-system acceptance.

## Next required action

The owner/clean-system operator supplies both Windows environments and the
supported image privately, receives the exact private candidates/audits, then
runs the checklist. No clean Windows 10 system or separate clean standard-account
Windows 11 environment is available through this repository session. The current
development host has an existing PSWaker installation, which is preserved.

Return filled records and reviewed sanitized exports through a chosen private
route. Keep installers, owner images, packages, raw logs and artifact reports
private. The agent reviews the returned identities, each scenario/retry,
preservation hashes, timings and limitations before changing acceptance status.
Missing clean environments or missed fault stages remain explicit gaps.

This private acceptance work is not blocked from starting by inherited
redistribution questions. Public distribution remains under #47/#50, and actual
console gameplay/package-update/save/settings acceptance remains #49. There is
no measured Windows duration guarantee or claim of acceptance for the bundled
native program from this handoff.
