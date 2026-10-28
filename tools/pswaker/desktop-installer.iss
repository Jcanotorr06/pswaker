; Maintainer-only compiler. No downloads, runtime bootstrappers or owner data.
#if Ver != EncodeVer(6, 7, 3)
  #error Use the pinned Inno Setup 6.7.3 compiler
#endif

[Setup]
AppId={{05802D72-13B7-4ABF-8FDE-7C917237D446}
AppName=PSWaker
AppVersion={#AppVersion}
AppPublisher=PSWaker
VersionInfoVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\PSWaker
DefaultGroupName=PSWaker
PrivilegesRequired=lowest
ArchitecturesAllowed=x64os
ArchitecturesInstallIn64BitMode=x64os
MinVersion=10.0
DisableDirPage=yes
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
UninstallDisplayIcon={app}\releases\{#ReleaseDirectory}\PSWaker.exe
OutputBaseFilename=PSWaker-{#AppVersion}-win-x64-setup
SetupIconFile=waker.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
AppMutex=PSWaker.Desktop.Offline
CloseApplications=no
RestartApplications=no
SetupLogging=yes

[Files]
; Versioned directories prevent mixing old/new runtimes. Inno records each
; installed file across manual updates and removes only those files on uninstall.
Source: "{#AppSource}\*"; DestDir: "{app}\releases\{#ReleaseDirectory}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\PSWaker"; Filename: "{app}\releases\{#ReleaseDirectory}\PSWaker.exe"; WorkingDir: "{app}\releases\{#ReleaseDirectory}"

[Run]
Filename: "{app}\releases\{#ReleaseDirectory}\PSWaker.exe"; Description: "Launch PSWaker"; Flags: nowait postinstall skipifsilent
