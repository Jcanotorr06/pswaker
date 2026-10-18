# Issue tracker: GitHub

Issues and specs live in GitHub Issues for
Jcanotorr06/windwaker-ps4. Use the gh CLI from this clone.

## Conventions

- Create: gh issue create --title "..." --body-file <file>
- Read: gh issue view <number> --json number,title,body,labels,comments
- List: gh issue list --state open --json number,title,body,labels
- Comment: gh issue comment <number> --body-file <file>
- Apply labels: gh issue edit <number> --add-label "<label>"
- Remove labels: gh issue edit <number> --remove-label "<label>"
- Close: gh issue close <number> --comment "..."

Use files containing actual newlines for multiline bodies.
Infer the repository from the Git remote.

## Pull requests as a triage surface

**PRs as a request surface: no.**

## Skill operations

When a skill says "publish to the issue tracker", create a GitHub issue.
When it says "fetch the relevant ticket", read the GitHub issue.

For parent-child work, use GitHub sub-issues when available.
Otherwise, add "Part of #<parent>" to the child and link it
in a task list in the parent.

Use native GitHub issue dependencies when available.
Otherwise, record "Blocked by: #<number>" in the issue body.
A ticket is unblocked when all blockers are closed.
