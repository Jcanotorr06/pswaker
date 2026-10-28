# Contributing to PSWaker

Thanks for helping. This page explains how to report problems and how to get a
change merged. The same rules apply to people and to automated agents; agents
also follow [AGENTS.md](AGENTS.md).

## Ground rule: no game data

Never commit, attach or upload any of the following, in code, tests, issues,
pull requests or logs:

- disc images (`.iso`, `.gcm`, `.rvz` and similar) or files extracted from them
- keys, signing material or credentials
- saves, memory-card files or console captures that contain game content
- complete packages (`.pkg`) or other build outputs
- personal paths, usernames or network details

[.gitignore](.gitignore) blocks the common file types; don't work around it.
Tests use synthetic, data-free fixtures in [tests/ps4](tests/ps4/).

## Reporting a problem

Open a [GitHub issue](https://github.com/Jcanotorr06/pswaker/issues). Include:

- the PSWaker desktop version and the program version shown in the app window
- your Windows version, and your PS4 model, firmware and GoldHEN version if the
  problem is on the console
- what you did, what you expected and what happened

For desktop failures, attach the JSON from **Export troubleshooting report…**.
It is built to leave out personal paths and game data. Don't attach the raw logs
under `%LOCALAPPDATA%\PSWaker\logs` or the files next to a package; they can
contain personal paths. See [private troubleshooting reports](docs/desktop/README.md#private-troubleshooting-reports).

### Triage labels

Maintainers use five triage labels, described in
[docs/agents/triage-labels.md](docs/agents/triage-labels.md):

| Label | Meaning |
| --- | --- |
| `needs-triage` | A maintainer needs to evaluate it |
| `needs-info` | Waiting for information from the reporter |
| `ready-for-agent` | Fully specified; ready to implement |
| `ready-for-human` | Needs a person, for example to test on a console |
| `wontfix` | Will not be actioned |

## Making a change

1. **Start from an issue.** Discuss larger changes in an issue before you write
   them, so the scope is agreed.
2. **Branch from `develop`.** Name the branch `<type>/<issue>-<name>`, or
   `<type>/<name>` when there's no issue. `<type>` is `bug`, `feature` or
   `docs`; `<name>` is short lowercase kebab-case. For example:
   `bug/42-fix-readback`, `feature/15-platform-verification`,
   `docs/agent-branching`.
3. **Commit only to your branch.** Never commit directly to `develop` or `main`.
   Write commit subjects in the imperative and reference the issue, for example
   `fix: handle desktop package storage failures (#43)`.
4. **Run the checks** (below) and make sure they pass.
5. **Open a pull request into `develop`.** Say what changed, why, how you tested
   it and what remains untested. Link the issue.

`main` only receives release merges; see [docs/RELEASING.md](docs/RELEASING.md).

## Checks

Linux or WSL2:

```bash
python3 -m compileall -q platform/ps4 tools/pswaker tests/ps4
python3 -m unittest discover -s tests/ps4
```

Windows desktop changes also need the Windows suite and Pyright. The commands
and prerequisites are in [BUILDING.md](BUILDING.md#checks). [CI](.github/workflows/ci.yml)
runs both suites on pull requests that touch code. Changes to the PS4 program
also need a target build; see [BUILDING.md](BUILDING.md).

## Console and owner evidence

Host checks can't show that something works on a PS4. Behaviour on the console is
accepted only through an owner-operated checklist in [docs/ps4](docs/ps4/) or
[docs/desktop](docs/desktop/), with the results recorded under
[evidence/ps4](evidence/ps4/).

- Evidence belongs to one exact build. A new build ID or changed packaging input
  needs new console results; it doesn't inherit an earlier pass.
- Retained evidence files are archived records. Don't edit or reformat them; add
  a new record instead.
- Keep failures and missing observations in the record. Don't replace them with a
  later success.
- Issues that wait on console testing carry `ready-for-human` and stay open until
  the returned evidence has been reviewed.

## Repository map

| Area | Contents |
| --- | --- |
| [tools/pswaker](tools/pswaker/) | Host commands: builds, packaging, desktop app and installer |
| [platform/ps4](platform/ps4/) | PS4 runtime, CMake/toolchain definitions, locks, patches, provenance and notices |
| [tests/ps4](tests/ps4/) | Python tests, native harnesses and synthetic fixtures |
| [docs/ps4](docs/ps4/README.md) | PS4 build guides and owner checklists |
| [docs/desktop](docs/desktop/README.md) | Desktop app guide and Windows checklists |
| [evidence/ps4](evidence/ps4/) | Retained checkpoint evidence |
| [GLOSSARY.md](GLOSSARY.md) | Project vocabulary; use these terms in issues and code |

## License

PSWaker is licensed under the [GNU General Public License v3.0](LICENSE). By
contributing, you agree that your contribution is licensed under the same
license. There is no contributor license agreement. Keep the license and notice
files of any third-party code you add, and record its source and license in the
relevant lock or provenance file.
