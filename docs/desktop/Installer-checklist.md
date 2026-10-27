# Offline installer acceptance

Use this checklist for #46 development-host observations and the separate #48
clean-system matrix. Do not mark a clean-system row from a development host.
Keep installers and all complete packages private until #47/#50 release gates
pass. Never attach an owner image, extracted content or complete package to a
public ticket.

| Environment | Candidate A | Candidate B | Standard account | Networking disabled before install |
| --- | --- | --- | --- | --- |
| Windows 10 x64, clean | pending | pending | pending | pending |
| Windows 11 x64, clean | pending | pending | pending | pending |

For each environment, retain the exact installer files and their corresponding
`installer-release.json` records. Record OS edition/build, account elevation,
installer SHA-256, app versions and installed `application-release.json` hashes.
The audit records include every bundled program/tool/runtime file identity,
program build/ELF/SELF hashes, content-contract hash and compiler recipe/closure.

1. Start with a standard Windows account and no PSWaker, Python, development
   runtime, .NET installation, SDK, repository, WSL, Docker or VM. Obtain the
   candidate installers and a supported image privately before disconnecting.
   Disable networking before installation and leave it disabled throughout.
2. Run candidate A normally. Confirm no administrator prompt, download, sign-in
   or prerequisite installer. Confirm the per-user Start menu shortcut and
   Installed apps entry. Launch from that shortcut with no developer PATH.
3. Record the visible app, program/build, tool revision/SDK and console baseline.
   Optionally run the installed read-only `--check-installation <new-json-path>`
   probe and retain its identities. Startup must reject missing/changed bundled
   inputs with reinstall guidance rather than finding tools elsewhere.
4. Record source-image SHA-256, select that image and a private custom output
   parent through the actual installed app, validate and create a complete
   package. Record the verified result, package SHA-256, SFO/content identity,
   inspection report and measured stage durations. Independently reinspect the
   retained package. Check the source-image hash is unchanged.
5. While the app remains open, attempt to install candidate B or uninstall. It
   must ask to close PSWaker or fail the silent operation, without killing active
   work. Complete/cancel work and close the app normally.
6. Run candidate B manually, still offline. Confirm one per-user application
   registration and the shortcut opening the new app version with its matching
   bundled program/tools. Repeat package creation at another custom destination
   and fresh independent inspection. Check candidate A's completed output and
   source image remain unchanged; app versions must not create a new console
   title/content identity. A desktop-only update can retain the same program
   version; test a program update separately in #49.
7. Uninstall from Windows Installed apps. Confirm installed app executables,
   bundled runtime files, shortcuts and app registration are removed. Confirm
   both completed outputs, original image and unrelated owner files survive,
   including those outside default folders. Untracked files inside the install
   location and local diagnostic/recovery state are intentionally preserved.
8. Record observations with the precise artifact identities and any failures.
   Leave #48 open for missing OS/account/offline evidence. Run #49's actual
   console update/save/settings checks separately; container success cannot
   establish that evidence.

This installer uses per-user registration and a stable installer AppId, as
described by [Inno Setup's non-administrative installation rules](https://jrsoftware.org/ishelp/topic_admininstallmode.htm)
and [update directory reuse](https://jrsoftware.org/ishelp/topic_setup_usepreviousappdir.htm).
Its `x64os` architecture restriction excludes ARM64 emulation, following
[Inno Setup's architecture definitions](https://jrsoftware.org/ishelp/topic_archidentifiers.htm).
