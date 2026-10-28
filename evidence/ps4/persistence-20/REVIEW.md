# Review against starting develop — issue #20

Fixed point: `7364a4fc197ae54ccd2ee4eba365dc9c9fb9754c`, the user-approved
develop commit used to create `feature/20-save-settings-persistence`.
Independent Standards and Spec agents reviewed the staged diff before commit,
using `git diff --cached <fixed-point>`. There were no implementation commits
yet. This follows the implementation workflow's review-before-commit order.

## Standards

No documented-standard violations or actionable baseline smells found. Branch
naming, glossary vocabulary, private-artifact handling, evidence limits and
separation of caches/user data follow the documented rules.

The initial review found one minor logging defect: the STORAGE line used
`Card_A,Card_B` instead of the actual `Card A` and `Card B` directory names.
The emitted paths were corrected. Follow-up review confirmed the correction
and found no remaining correctness findings in those deltas.

The follow-up also checked the strengthened menu test, which now writes and
reloads real temporary profile data, and the post-rename directory-sync failure
test. That test correctly distinguishes reported failure/retained in-memory
state from the newly visible file. Provisional artifact evidence was excluded
from the initial review until build and package completion.

## Spec

No actionable Spec findings. Actual card channels explicitly select GCI and the
shared writable root. Startup checks real card directories and settings before
gameplay, with actionable Retry/Exit. Settings preserve unrelated content and
report failed writes. GCI replacement checks file/directory synchronization;
save readback and metadata errors propagate to existing failure handling.
Normal Quit retains its pending-card observer without requesting a game save.

No scope creep found: the text-size setting implements the requested observable
persistent setting. Broader backup/corruption recovery and controlled pending-
write acceptance remain #21. Uncertainty after rename followed by failed
directory synchronization is reported as failure without claiming rollback.

Hardware acceptance remains partial and explicitly pending: “Owner fully closes
and relaunches” and “Separately install an updated complete package” require
returned observations associated with the installed binary. The checklist
distinguishes those tests and protects real progress; host tests cannot satisfy
them. This checkpoint must not close #20 before the owner return is reviewed.

The final independent Spec consistency check passed after artifact completion.
Both inspection records agree with artifacts.json on package hashes, sizes,
versions, application IDs, build ID, ELF/SELF and image hashes. All recorded
port-input hashes match current files; the ABI record identifies the same ELF.
The host log contains 48 passing tests with zero skips, and host recovery
records restoration of current zlib `.2.3`. The completed report/checklist
retain hardware-pending status and require separate relaunch and 01.08 install
observations without overwriting real progress.

Standards: 0 outstanding violations/smells/correctness findings after correction.
Spec: 0 actionable findings; hardware completion still requires owner evidence.
