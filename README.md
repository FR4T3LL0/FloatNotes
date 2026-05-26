# FloatNotes

FloatNotes ist eine lokale Windows-Desktop-App für persönliche Notizen. Die App läuft offline, benötigt kein Benutzerkonto und speichert Daten lokal als JSON unter dem Windows-Benutzerprofil.

## Status

Aktueller Stand: erste Windows-Release-Vorbereitung.

- PySide6-Desktop-App mit modernem Hauptfenster.
- Floating-Icon als kleiner Always-on-top-Launcher.
- Notizen-Listen mit stichpunktartigen Einträgen.
- CRUD für Listen und Stichpunkte.
- Erledigt-Status pro Stichpunkt.
- Debounced Auto-Save nach Änderungen.
- Backup-Rotation und Recovery-Logik für JSON-Dateien.
- Eigenes App-/EXE-Icon.
- System-Tray-Icon für erwartbares Windows-Verhalten.
- Tastaturkürzel für häufige Aktionen.
- Optionaler Windows-Autostart über bewusste Aktivierung.
- Dokumentation, Release-Checkliste, Installer-Skripte und Tests.

## Tech-Stack

- Python 3.12+
- PySide6 für die Desktop-Oberfläche
- JSON für lokale Speicherung
- pathlib für Dateipfade
- dataclasses für Datenmodelle
- unittest und pytest für Tests
- PyInstaller für den Windows-EXE-Build
- Inno Setup für den Windows-Installer

## Download und Installation

Für normale Nutzer ist der Installer das empfohlene Artefakt:

```text
https://github.com/FR4T3LL0/FloatNotes/releases/latest
```

Direkter Installer-Download:

```text
https://github.com/FR4T3LL0/FloatNotes/releases/latest/download/FloatNotesSetup.exe
```

```text
FloatNotesSetup.exe
```

Bei einem unsignierten Build kann Windows SmartScreen eine Warnung anzeigen.
Das ist bei kleinen Open-Source-Projekten ohne Code-Signing-Zertifikat
erwartbar. Für weniger Warnungen muessen `FloatNotes.exe` und
`FloatNotesSetup.exe` vor dem Release signiert werden.

## Entwicklungsumgebung einrichten

PowerShell im Projektverzeichnis:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Falls PowerShell die Aktivierung blockiert:

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

Beim Start erscheint zuerst das Floating-Icon. Ein Linksklick zeigt oder versteckt das Hauptfenster.

## Bedienung

- `Neue Liste`: Erstellt eine neue Notizen-Liste.
- `Umbenennen`: Benennt die ausgewählte Liste um.
- `Löschen`: Löscht die ausgewählte Liste oder den ausgewählten Stichpunkt nach Bestätigung.
- Eingabefeld unten: Fuegt einen Stichpunkt zur ausgewählten Liste hinzu.
- Checkbox am Stichpunkt: Markiert einen Stichpunkt als erledigt oder offen.
- `Bearbeiten` oder Doppelklick auf einen Stichpunkt: ändert den Text.
- Floating-Icon links ziehen: Verschiebt den Launcher und speichert die Position.
- Rechtsklick auf das Floating-Icon: öffnen/Ausblenden, Autostart aktivieren/deaktivieren oder App beenden.
- Das Floating-Icon bleibt beim Ziehen vollständig innerhalb der sichtbaren Bildschirmfläche.
- Hover und Drag am Floating-Icon nutzen dezente Opacity-Animationen für ein hochwertigeres Feedback.
- System-Tray-Icon: Linksklick zeigt/versteckt das Hauptfenster; Rechtsklick bietet Öffnen, Ausblenden, Floating-Icon anzeigen und Beenden.

## Tastaturkuerzel

- `Ctrl+N`: Neue Liste erstellen.
- `F2`: Ausgewählte Liste umbenennen.
- `Ctrl+Return`: Stichpunkt hinzufuegen.
- `Ctrl+E`: Ausgewählten Stichpunkt bearbeiten.
- `Delete`: Ausgewählten Stichpunkt löschen.
- `Ctrl+F`: Eingabefeld fokussieren.
- `Esc`: Hauptfenster ausblenden.

## Tests ausfuehren

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\Activate.ps1
.\tools\quality_check.ps1
```

Der Quality-Check fuehrt `ruff check`, `ruff format --check`, `pytest` und `compileall` aus. Einzelne Tests können weiterhin direkt gestartet werden:

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Syntaxcheck:

PowerShell im Projektverzeichnis:

```powershell
python -m compileall app tests
```

## Lokale Speicherung

Produktive Notizen:

```text
%APPDATA%\FloatNotes\notes.json
```

Backups und Recovery-Dateien:

```text
%APPDATA%\FloatNotes\notes.backup-YYYYMMDD-HHMMSS-ffffff.json
%APPDATA%\FloatNotes\notes.corrupt-YYYYMMDD-HHMMSS-ffffff.json
```

Lokale UI-Einstellungen:

```text
%APPDATA%\FloatNotes\settings.json
```

`settings.json` speichert aktuell die Position des Floating-Icons.

## Projektstruktur

```text
FloatNotes/
|-- app/
|   |-- main.py
|   |-- core/
|   |   |-- app_paths.py
|   |   |-- autostart.py
|   |   |-- models.py
|   |   |-- settings.py
|   |   |-- single_instance.py
|   |   |-- storage.py
|   |-- ui/
|   |   |-- app_icon.py
|   |   |-- floating_icon.py
|   |   |-- geometry.py
|   |   |-- main_window.py
|   |   |-- styles.py
|   |   |-- task_row.py
|   |   |-- texts.py
|   |   |-- tray_icon.py
|   |   |-- widgets.py
|   |-- assets/
|   |   |-- floatnotes.ico
|-- installer/
|   |-- FloatNotes.iss
|-- tests/
|   |-- test_autostart.py
|   |-- test_geometry.py
|   |-- test_models.py
|   |-- test_project_structure.py
|   |-- test_settings.py
|   |-- test_single_instance.py
|   |-- test_storage.py
|   |-- test_ui_smoke.py
|-- tools/
|   |-- build_installer.ps1
|   |-- build_windows.ps1
|   |-- create_icon.py
|   |-- quality_check.ps1
|   |-- sign_windows.ps1
|   |-- smoke_test_installer.ps1
|   |-- sync_version.py
|-- .github/
|   |-- workflows/
|   |   |-- ci.yml
|-- README.md
|-- LICENSE
|-- build_instructions.md
|-- release_checklist.md
|-- FloatNotes.spec
|-- requirements.txt
|-- pyproject.toml
```

## Architektur

- `app/main.py`: Startet QApplication, Storage, Settings, Hauptfenster, Floating-Icon und System-Tray-Icon.
- `app/core/models.py`: Datenmodelle für Listen und Stichpunkte.
- `app/core/storage.py`: Robuste JSON-Speicherung mit Backup und Recovery.
- `app/core/settings.py`: Lokale UI-Einstellungen.
- `app/core/app_paths.py`: Windows-kompatible AppData-Pfade.
- `app/core/autostart.py`: Optionaler Windows-Autostart ueber den Current-User-Run-Key.
- `app/core/single_instance.py`: Verhindert mehrere parallele App-Instanzen.
- `app/ui/main_window.py`: Hauptfenster, Anzeige und CRUD-Koordination.
- `app/ui/floating_icon.py`: Always-on-top-Launcher mit Drag und Toggle.
- `app/ui/geometry.py`: Testbare Positionslogik für Fensterbegrenzung.
- `app/ui/app_icon.py`: Icon-Pfade für Source- und PyInstaller-Betrieb.
- `app/ui/tray_icon.py`: Windows-System-Tray-Integration.
- `app/ui/task_row.py`: Eigene Zeilenkomponente für Stichpunkte.
- `app/ui/texts.py`: Zentrale UI-Texte.
- `app/ui/styles.py`: Zentrales Qt-Stylesheet.
- `app/ui/widgets.py`: Kleine UI-Helfer.

## Design-Stand

Die UI nutzt eine ruhige Windows-taugliche, Apple-inspirierte Optik: helle Glasflächen, weiche Rundungen, dezente Schatten, klare Status-Badges, neutrale Hintergrundfarben und sparsame blaue Akzente für primäre Aktionen. Die aktive Liste wird mit Akzentbalken und Zähl-Badge hervorgehoben, erledigte Listen zeigen `Alles erledigt`, und der Eingabebereich ist als klarer Footer des Notizen-Panels gestaltet.

## EXE-Build

Der PyInstaller-Build erzeugt die gebaute EXE unter:

```text
dist\FloatNotes\FloatNotes.exe
```

PowerShell im Projektverzeichnis:

```powershell
.\tools\build_windows.ps1
```

Der Build nutzt `FloatNotes.spec` als versioniertes Build-Rezept, bindet `app\assets\floatnotes.ico` ein und schliesst ungenutzte Qt-Module, Qt-Plugins und Qt-Translations aus. Details stehen in `build_instructions.md`.

## Installer und Release-Artefakte

Installer bauen:

```powershell
.\tools\build_installer.ps1
```

Ergebnis:

```text
installer_output\FloatNotesSetup.exe
```

Installer technisch pruefen:

```powershell
.\tools\smoke_test_installer.ps1
```

Das Artefakt aus `installer_output\` ist für GitHub Releases gedacht.
`build\` und `dist\` bleiben lokale Build-Artefakte.

## Autostart unter Windows

Autostart wird nicht automatisch aktiviert. Er kann bewusst ueber das Floating-Icon aktiviert werden:

1. FloatNotes starten.
2. Rechtsklick auf das Floating-Icon.
3. `Autostart aktivieren` wählen.
4. Den Bestätigungsdialog pruefen und bestätigen.

Die App schreibt dann für den aktuellen Windows-Benutzer diesen Registry-Wert:

```text
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
Name: FloatNotes
Wert: "<Installationspfad>\FloatNotes.exe"
```

Deaktivieren erfolgt ebenfalls ueber Rechtsklick auf das Floating-Icon und `Autostart deaktivieren`.

## Lizenz

FloatNotes steht unter der MIT-Lizenz. Details stehen in `LICENSE`.
