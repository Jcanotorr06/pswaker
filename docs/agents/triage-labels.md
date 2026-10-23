# Triage labels

| Role | Tracker label | Meaning |
| --- | --- | --- |
| needs-triage | needs-triage | Maintainer evaluation needed |
| needs-info | needs-info | Waiting for reporter information |
| ready-for-agent | ready-for-agent | Fully specified for an agent |
| ready-for-human | ready-for-human | Requires human implementation or validation |
| wontfix | wontfix | Will not be actioned |

Use this mapping whenever a skill names a triage role.

When the next required action is human implementation or validation, replace
`ready-for-agent` with `ready-for-human`. Keep the issue open until the required
human work or validation evidence is complete. A merged PR or passing host
checks alone do not complete an issue that requires human validation.
