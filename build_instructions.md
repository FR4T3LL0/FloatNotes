# Build-Anleitung fuer FloatNotes

Diese Datei beschreibt Entwicklung, Test, Windows-Build, Installer und Release-Artefakte. Der PyInstaller-Build nutzt ein versioniertes Spec-Rezept mit App-Icon und reduzierten Qt-Abhaengigkeiten.

## Voraussetzungen

- Windows
- Python 3.12 oder neuer
- PyCharm oder ein PowerShell-Terminal
- Geklontes Projektverzeichnis

## Entwicklungsumgebung einrichten

PowerShell im Projektverzeichnis:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Falls PowerShell die Aktivierung der virtuellen Umgebung verhindert:

PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## App im Entwicklungsmodus starten

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.main
```

Erwartetes Verhalten:

- Das Floating-Icon erscheint zuerst.
- Linksklick auf das Icon zeigt oder versteckt das Hauptfenster.
- Rechtsklick auf das Icon zeigt ein Menue mit Oeffnen/Ausblenden, Autostart und Beenden.

## Quality Gate

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\Activate.ps1
.\tools\quality_check.ps1
```

Der Quality-Check fuehrt aus:

- `ruff check app tests`
- `ruff format --check app tests`
- `pytest -p no:cacheprovider`
- `python -m compileall app tests`

Einzelne Tests koennen weiterhin direkt gestartet werden:

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Syntaxcheck:

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\python.exe -m compileall app tests
```

## EXE-Build

Der Build wird ueber das versionierte PyInstaller-Spec-Rezept `FloatNotes.spec` ausgefuehrt. Vor dem Build synchronisiert `tools\build_windows.ps1` die Installer-Version aus `pyproject.toml` nach `installer\FloatNotes.iss`.

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\Activate.ps1
.\tools\build_windows.ps1
```

Der Build erzeugt:

```text
build/
dist/
```

Die ausfuehrbare App liegt danach unter:

```text
dist\FloatNotes\FloatNotes.exe
```

Gepruefter Build-Stand:

- `dist\FloatNotes\FloatNotes.exe` wurde erzeugt.
- `FloatNotes.spec` ist bewusst versioniert und enthaelt Icon, Add-Data und Excludes.
- `build\` und `dist\` bleiben lokale Build-Artefakte und sind in `.gitignore` ausgeschlossen.
- Der Build schliesst ungenutzte Qt-Module und Qt-Plugins aus und entfernt Qt-Translations aus den PyInstaller-Daten.
- EXE-Groesse: ca. 1.8 MB.
- Gesamtgroesse `dist\FloatNotes`: ca. 86.6 MB nach Plugin-/Translation-Filterung.
- Qt-Plugins im Build: `platforms\qwindows.dll`, `imageformats\qico.dll`, `styles\qmodernwindowsstyle.dll`.
- Smoke-Test: EXE wurde gestartet, blieb lauffaehig und legte unter einem umgeleiteten `APPDATA` eine `notes.json` an.
- Nach der Optimierungsrunde wurde die EXE erneut gebaut und per Smoke-Test geprueft.

Die PyInstaller-Warnungen betreffen plattformabhaengige optionale Module wie Unix-Module (`pwd`, `grp`, `fcntl`) und sind fuer die Windows-App nicht relevant.

## App-Icon

Das Icon liegt unter:

```text
app\assets\floatnotes.ico
```

Falls es fehlt, kann es neu erzeugt werden:

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\python.exe tools\create_icon.py
```

`tools\build_windows.ps1` erzeugt das Icon automatisch neu, falls die Datei vor dem Build fehlt.

## Datenpfade im EXE-Betrieb

Die App speichert Nutzdaten nicht im `dist`-Ordner, sondern im Benutzerprofil.

Produktive Notizen:

```text
%APPDATA%\FloatNotes\notes.json
```

Backups und Recovery-Dateien:

```text
%APPDATA%\FloatNotes\notes.backup-YYYYMMDD-HHMMSS-ffffff.json
%APPDATA%\FloatNotes\notes.corrupt-YYYYMMDD-HHMMSS-ffffff.json
%APPDATA%\FloatNotes\settings.corrupt-YYYYMMDD-HHMMSS-ffffff.json
```

Floating-Icon-Position:

```text
%APPDATA%\FloatNotes\settings.json
```

## Build-Artefakte bereinigen

PowerShell im Projektverzeichnis:

```powershell
Remove-Item -Recurse -Force build, dist
```

Diesen Befehl nur ausfuehren, wenn die lokalen Build-Artefakte wirklich geloescht werden sollen. `FloatNotes.spec` bleibt erhalten, weil es bewusst versioniert wird.

## Autostart

Autostart wird nicht ungefragt aktiviert. FloatNotes hat eine vorbereitete Current-User-Registry-Integration, die nur nach ausdruecklicher Bestaetigung aus dem Floating-Icon-Menue schreibt.

Verwendeter Registry-Pfad:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
Name: FloatNotes
```

Manueller Status-Check:

Terminal: PowerShell  
Pfad: beliebig

```powershell
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "FloatNotes"
```

Manuelles Entfernen nur bei Bedarf:

Terminal: PowerShell  
Pfad: beliebig

```powershell
Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "FloatNotes"
```

Alternative ohne Registry bleibt der Windows Startup-Ordner:

Terminal: Windows Ausfuehren oder Explorer-Adresszeile  
Pfad: beliebig

```text
shell:startup
```

Dort kann bei Bedarf manuell eine Verknuepfung auf `FloatNotes.exe` abgelegt werden.

## Installer

Der Installer wird mit Inno Setup gebaut. Die App installiert sich bewusst ohne Administratorrechte unter dem aktuellen Benutzerprofil:

```text
%LOCALAPPDATA%\Programs\FloatNotes
```

Voraussetzung: Inno Setup 6 muss installiert sein und `ISCC.exe` muss im PATH oder in einem Standardpfad liegen.

PowerShell im Projektverzeichnis:

```powershell
.\tools\build_installer.ps1
```

Erwartetes Ergebnis:

```text
installer_output\FloatNotesSetup.exe
```

Technischer Installer-Smoke-Test mit isoliertem Installationsziel:

PowerShell im Projektverzeichnis:

```powershell
.\tools\smoke_test_installer.ps1
```

Der Smoke-Test installiert nach `.installer_smoke\FloatNotes`, startet die installierte EXE mit umgeleitetem `APPDATA`, prueft `notes.json` und deinstalliert wieder. Der Test nutzt `/NOICONS`, damit keine echten Desktop- oder Startmenue-Verknuepfungen im Benutzerprofil angelegt werden.

Optional kann die echte Desktop-Verknuepfung bewusst mitgeprueft werden:

PowerShell im Projektverzeichnis:

```powershell
.\tools\smoke_test_installer.ps1 -CheckDesktopShortcut
```

Dieser Modus bricht ab, wenn bereits `FloatNotes.lnk` auf dem Desktop existiert, damit keine vorhandene Verknuepfung ueberschrieben wird.

## Release-ZIP

Fuer eine portable Weitergabe ohne Installer kann ein versioniertes ZIP erzeugt werden:

PowerShell im Projektverzeichnis:

```powershell
.\tools\package_release.ps1
```

Das Skript liest die Version aus `pyproject.toml`, baut die EXE neu und erzeugt:

```text
release_output\FloatNotes-<version>-win64.zip
```

## Signierung

Fuer eine Weitergabe ausserhalb des eigenen Rechners sollte zusaetzlich Code-Signing geprueft werden. Ohne Zertifikat kann Windows SmartScreen Warnungen anzeigen.

Voraussetzungen:

- Windows SDK mit `signtool.exe` oder `signtool.exe` im PATH.
- Code-Signing-Zertifikat als PFX-Datei oder Zertifikat im Windows-Zertifikatsspeicher.
- PFX-Dateien duerfen nicht ins Repository; `.gitignore` schliesst `*.pfx`, `*.p12` und `certs/` aus.

Signieren mit PFX:

PowerShell im Projektverzeichnis:

```powershell
$env:FLOATNOTES_SIGNING_PASSWORD = "<PFX-PASSWORT>"
.\tools\sign_windows.ps1 -CertificatePath "C:\Pfad\zum\codesigning.pfx"
Remove-Item Env:\FLOATNOTES_SIGNING_PASSWORD
```

Signieren mit Zertifikat aus dem Windows-Zertifikatsspeicher:

PowerShell im Projektverzeichnis:

```powershell
.\tools\sign_windows.ps1 -CertificateThumbprint "<SHA1-THUMBPRINT>"
```

Standardmaessig signiert und verifiziert das Skript:

```text
dist\FloatNotes\FloatNotes.exe
installer_output\FloatNotesSetup.exe
```

Einzelne Ziele koennen mit `-Targets` uebergeben werden.

## Release-Prozess

Die kompakte Release-Checkliste liegt in:

```text
release_checklist.md
```
