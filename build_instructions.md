# Build-Anleitung fuer FloatNotes

Diese Datei beschreibt Entwicklung, Test und den Windows-Build. Der PyInstaller-Build wurde in Phase 8 erstellt und in der Optimierungsrunde auf ein versioniertes Spec-Rezept mit App-Icon und reduzierten Qt-Abhaengigkeiten umgestellt.

## Voraussetzungen

- Windows
- Python 3.12 oder neuer
- PyCharm oder ein PowerShell-Terminal
- Projektpfad: `C:\Users\marco\dev\FloatNotes`

## Entwicklungsumgebung einrichten

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Falls PowerShell die Aktivierung der virtuellen Umgebung verhindert:

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## App im Entwicklungsmodus starten

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.main
```

Erwartetes Verhalten:

- Das Floating-Icon erscheint zuerst.
- Linksklick auf das Icon zeigt oder versteckt das Hauptfenster.
- Rechtsklick auf das Icon zeigt ein Menue mit Oeffnen/Ausblenden, Autostart und Beenden.

## Quality Gate

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

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

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Syntaxcheck:

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
.\.venv\Scripts\python.exe -m compileall app tests
```

## EXE-Build

Der Build wird ueber das versionierte PyInstaller-Spec-Rezept `FloatNotes.spec` ausgefuehrt. Vor dem Build synchronisiert `tools\build_windows.ps1` die Installer-Version aus `pyproject.toml` nach `installer\FloatNotes.iss`.

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

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

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

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

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

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

Dort kann spaeter manuell eine Verknuepfung auf `dist\FloatNotes\FloatNotes.exe` abgelegt werden.

## Installer und Signierung

Ein Inno-Setup-Skript ist vorbereitet:

```text
installer\FloatNotes.iss
```

Der Installer wird nicht automatisch gebaut, weil dafuer Inno Setup lokal installiert sein muss. Fuer eine Weitergabe ausserhalb des eigenen Rechners sollte zusaetzlich Code-Signing geprueft werden. Ohne Zertifikat kann Windows SmartScreen Warnungen anzeigen.

## Release-Prozess

Die kompakte Release-Checkliste liegt in:

```text
release_checklist.md
```
