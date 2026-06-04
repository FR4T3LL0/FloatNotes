; Inno Setup script template for FloatNotes.
; Requires Inno Setup to be installed separately.

#define MyAppName "FloatNotes"
; Synchronized from pyproject.toml via tools\sync_version.py.
#define MyAppVersion "0.1.2"
#define MyAppPublisher "FloatNotes"
#define MyAppExeName "FloatNotes.exe"

[Setup]
AppId={{76E62E4D-7C12-4C95-A54B-4FAE5F6FD84E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\installer_output
OutputBaseFilename=FloatNotesSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\FloatNotes\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "startmenuicon"; Description: "Startmenue-Verknuepfung erstellen"; GroupDescription: "Optionale Verknuepfungen:"; Flags: checkedonce
Name: "desktopicon"; Description: "Desktop-Verknuepfung erstellen"; GroupDescription: "Optionale Verknuepfungen:"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} starten"; Flags: nowait postinstall skipifsilent
