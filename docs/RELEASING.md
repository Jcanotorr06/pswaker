# Releasing PSWaker

This is the maintainer process for publishing a desktop release. It follows
git-flow: work collects on `develop`, a `release/<version>` branch prepares the
release, and `main` receives only release merges, each one tagged.

A release publishes the Windows app and installer. It never publishes disc
images, extracted game files, keys or complete packages. Making a release
**public** also needs a passing readiness decision in
[#50](https://github.com/Jcanotorr06/pswaker/issues/50). Until then, releases are
pre-releases in the private repository.

## Versions

| Item | Form | Example |
| --- | --- | --- |
| Release version | `X.Y.Z` (SemVer) | `0.1.0` |
| Release candidate tag | `vX.Y.Z-rc.N` | `v0.1.0-rc.1` |
| Final release tag | `vX.Y.Z` | `v0.1.0` |
| Release branch | `release/X.Y.Z` | `release/0.1.0` |
| Windows app version | `X.Y.Z.N`: `N` is the RC number, `100` for the final release | `0.1.0.1` for RC1, `0.1.0.100` for the final release |
| Console program version | `NN.NN`, independent of the release version | `01.13` |

No file in the repository holds the release version. It lives in the tag, the
release-notes filename and the `--app-version` passed to the build. All RCs of
one version, and its final release, come from the same release branch.

## Before you start

- Open a tracking issue for the release with its scope, bundled program and
  known issues.
- Check that `develop` passes CI and that the README's status and known issues
  are current.
- Choose the **program release** to bundle and record its build ID. Bundling an
  existing, console-tested program release keeps its evidence valid. A rebuilt
  program is a new binary that needs new console evidence; see
  [BUILDING.md](../BUILDING.md).
- Have the Windows prerequisites from [BUILDING.md](../BUILDING.md#prerequisites)
  ready. Keep every build output outside the repository, for example under
  `C:\private\release-X.Y.Z-rc.N\`.

## 1. Cut the release branch

```bash
git switch develop && git pull --ff-only
git switch -c release/0.1.0
```

Commit only release preparation to this branch: the release notes, version
references and last fixes. For a later RC, add fixes to the same branch.

## 2. Write the release notes

Add `docs/release-notes/vX.Y.Z-rc.N.md`, starting from the previous release's
notes. Include these sections:

1. **Summary**: what this release is and who it is for.
2. **Assets**: each file and what it is for.
3. **Tested platform**: console, firmware, GoldHEN, disc and Windows versions.
4. **Requirements and quick start**: a short version of the README, with a link.
5. **Known issues**: the README list, adjusted for this release.
6. **Not included**: no game data, disc images, keys or complete packages.
7. **Identities**: console program version and build ID, ELF/SELF SHA-256,
   LibOrbisPkg revision, .NET SDK, Python and PyInstaller versions.
8. **Disclaimer**: the README disclaimer.

Asset checksums aren't in the notes file, because they're known only after the
build. Step 6 appends them to the published notes.

Push the branch and open a pull request into `main`:

```bash
git push -u origin release/0.1.0
gh pr create --base main --head release/0.1.0 --title "Release 0.1.0 RC1"
```

## 3. Merge into `main`

After review, merge with a **merge commit**. Don't squash or rebase, so `main`
keeps the history of `develop`:

```bash
gh pr merge <number> --merge
git fetch origin
git rev-parse origin/main   # the release commit; record it
```

## 4. Build the assets

Build in a separate worktree at the release commit so local changes can't leak
in:

```powershell
git worktree add C:\private\pswaker-0.1.0-rc.1 origin/main
cd C:\private\pswaker-0.1.0-rc.1
$out = 'C:\private\release-0.1.0-rc.1'
$program = 'C:\private\program-release-01.13'
$version = '0.1.0.1'

python -m pip install -r tools/pswaker/desktop-requirements.txt
python tools/pswaker/prepare-windows-tools.py --dotnet (Get-Command dotnet).Source --output "$out\windows-tools"
python tools/pswaker/build-desktop.py --program $program --packaging "$out\windows-tools" --app-version $version --output "$out\desktop"
python tools/pswaker/build-installer.py --program $program --packaging "$out\windows-tools" --app-version $version --iscc 'C:\maintainer\Inno Setup 6\ISCC.exe' --output "$out\installer"
```

Check the program release's build ID in `$program\program-release.json`
against the one you chose. Then collect the assets:

```powershell
$assets = "$out\assets"
New-Item -ItemType Directory $assets | Out-Null
Copy-Item "$out\installer\PSWaker-$version-win-x64-setup.exe" $assets
Copy-Item "$out\installer\installer-release.json" "$assets\PSWaker-$version-installer-release.json"
tar -a -c -f "$assets\PSWaker-$version-win-x64-portable.zip" -C "$out\desktop" PSWaker
Get-ChildItem $assets -File | Where-Object Name -ne 'SHA256SUMS.txt' | Sort-Object Name |
  ForEach-Object { '{0}  {1}' -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), $_.Name } |
  Set-Content -Encoding ascii "$assets\SHA256SUMS.txt"
```

| Asset | Contents |
| --- | --- |
| `PSWaker-<version>-win-x64-setup.exe` | Per-user installer |
| `PSWaker-<version>-win-x64-portable.zip` | The self-contained `PSWaker` app folder |
| `PSWaker-<version>-installer-release.json` | Installer audit manifest: hashes, inventories, versions |
| `SHA256SUMS.txt` | SHA-256 of every other asset, in `sha256sum` format |

Never attach a `.pkg`, a separate ELF/SELF, a disc image or any other game data.

Before publishing, verify the assets:

- The installer's SHA-256 matches `installer.sha256` in its audit manifest.
- `SHA256SUMS.txt` matches every asset (`sha256sum -c SHA256SUMS.txt` in Git
  Bash).
- Extract the zip into a new folder and run
  `PSWaker.exe --check-installation <new report path>`. It must return zero.
- Optionally install and open the app on the build machine and check the
  version and baseline shown in the window.

Remove the worktree when you're done (`git worktree remove`).

## 5. Tag the release

Create an annotated tag on the release commit from step 3 and push it:

```bash
git tag -a v0.1.0-rc.1 -m "PSWaker 0.1.0 RC1" <release commit>
git push origin v0.1.0-rc.1
```

Tags are never moved or reused. If an asset needs fixing, publish a new RC.

## 6. Publish the GitHub release

Append the checksums to the notes, then create the release. Use `--prerelease`
for every RC:

```powershell
$notes = "$out\release-notes.md"
Get-Content docs\release-notes\v0.1.0-rc.1.md | Set-Content -Encoding utf8 $notes
Add-Content -Encoding utf8 $notes "`n## SHA-256 checksums`n`n``````text"
Get-Content "$assets\SHA256SUMS.txt" | Add-Content -Encoding utf8 $notes
Add-Content -Encoding utf8 $notes '```'

gh release create v0.1.0-rc.1 --verify-tag --prerelease --title "PSWaker 0.1.0 RC1" `
  --notes-file $notes (Get-ChildItem $assets -File).FullName
```

Open the release page and check that every asset is present and its size matches.

## 7. Merge back into `develop`

`develop` is updated only through pull requests, including for the back-merge:

```bash
gh pr create --base develop --head main --title "Merge release 0.1.0 RC1 back into develop"
gh pr merge <number> --merge
```

Keep `release/X.Y.Z` until that version's final release, then delete it.

## 8. After publishing

- Comment the release's identities (installer and portable SHA-256, app
  version, program build ID, tool revision) on each issue that tests this
  candidate. Change issue states only when their evidence supports it.
- Close the tracking issue after the release is published and the back-merge is
  merged.
- Keep the build outputs and audit manifests privately. They identify the exact
  bytes that testers received.

## Final releases

A final release follows the same steps with tag `vX.Y.Z`, app version
`X.Y.Z.100` and no `--prerelease`. Publish it only when the release gates for
that version have passed, and make the repository or release public only after
[#50](https://github.com/Jcanotorr06/pswaker/issues/50) records a passing
readiness decision.
