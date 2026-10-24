## Branching

Before making changes, create and check out a task branch from `develop`.
Continue on that branch for follow-up work on the same task. Commit changes
only to the task branch; never commit directly to `develop`.

Name branches `<type>/<issue>-<name>`, or `<type>/<name>` when no issue exists:

- `<type>` is `bug`, `feature`, or `docs`.
- `<issue>` is the GitHub issue number without `#`; omit it and the following
  hyphen when no issue exists.
- `<name>` is a short lowercase kebab-case description.

Examples: `bug/42-fix-readback`, `feature/15-platform-verification`,
`docs/agent-branching`.

Before committing, verify that the current branch is the task branch.

## Agent skills

### Issue tracker

Issues live in GitHub Issues. Read `docs/agents/issue-tracker.md`
before reading or publishing tickets.

### Triage labels

Use the five default triage labels. Read
`docs/agents/triage-labels.md` before applying triage labels.

### Domain docs

Single-context layout. Read `docs/agents/domain.md`
before exploring the codebase.
