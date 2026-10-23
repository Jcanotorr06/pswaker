# Implementation review

Fixed point: `2f01b198c644b4b462576f634ca4943b99c4223b`, approved by the owner.
The code-review skill ran separate Standards and Spec agents against the staged
implementation (`git diff --cached 2f01b19`), followed by a Spec review of the
dependency correction. There were no prior implementation commits at review time.

## Standards

No documented-standard violations found against AGENTS.md,
docs/agents/domain.md, GLOSSARY.md or CLAUDE.md. No relevant ADRs exist.

Two nonblocking judgment calls remain:

- **Possible Duplicated Code:** the standalone input, SDK, packaging, inspection,
  closure and audit tools each contain the same small SHA-256 file helper.
- **Possible Duplicated Code:** the inherited GPU completion loops in
  probe/main.cpp, probe/white-readback.hpp and probe/gx-setup.hpp repeat bounded
  event-processing/wait behavior. A shared helper could align future changes.

These are refactoring suggestions, not documented-standard breaches. The small
standalone CLI helpers and inherited GPU behavior remain identifiable in this
preparation change.

## Spec

One P1 finding was corrected: Aurora/FreeType linked SDK libpng and bzip2
archives while the initial maintained SDK-support script rebuilt neither.
The scripts now fetch the exact recipe-matched sources, compile both with Clang
21 and `btver2`, replace both regular SDK libpng archive names and generated
headers, and install rebuilt bzip2. Their hashes are retained. The documentation's
earlier claim that these archives were unused was corrected.

The follow-up review found no unresolved implementation defects or scope creep.
The later SDK ZIP symlink correction and its CLI regression received a separate
narrow Spec review, which also found no issues.
The selected preparation order, immutable closure, runtime contracts, diagnostic
checks, licensing uncertainties and distinction between historical and new
hardware evidence are preserved. The remaining SDK compatibility archives are
empty; inherited import stubs/sample modules remain explicit audited inputs.

The clean build and package inspection subsequently passed, along with all six
CLI tests. The final workspace matches the frozen compiled inputs. See the
accompanying [build report](REPORT.md) for the final verification result.
Both reviewers checked the final documentation/evidence. Standards found no
additional violations; Spec independently rehashed the retained PKG, ELF and
SELF, confirmed the completed clean-build log, and found no remaining #13
acceptance issues.
The maintained clean-build pair and renewed hardware gate remain assigned to #15.

Standards: **0 hard violations, 2 nonblocking duplication findings**.
Spec: **1 resolved P1, 0 unresolved implementation findings**.
