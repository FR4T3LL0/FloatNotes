# FloatNotes

FloatNotes ist eine lokale Windows-Desktop-App fuer persoenliche Notizen und Aufgabenlisten. Die App laeuft offline, benoetigt kein Benutzerkonto und speichert Daten lokal im Windows-Benutzerprofil.

## Funktionen

- Listen mit Stichpunkten erstellen, umbenennen und loeschen
- Stichpunkte hinzufuegen, bearbeiten, loeschen und als erledigt markieren
- Floating-Icon als kleiner Always-on-top-Launcher
- System-Tray-Icon fuer Oeffnen, Ausblenden und Beenden
- Automatisches lokales Speichern mit Backup- und Recovery-Logik
- Optionaler Windows-Autostart

## Installation

Der Installer ist ueber die aktuellen GitHub Releases verfuegbar:

```text
https://github.com/FR4T3LL0/FloatNotes/releases/latest
```

Direkter Installer-Download:

```text
https://github.com/FR4T3LL0/FloatNotes/releases/latest/download/FloatNotesSetup.exe
```

## Bedienung

- Linksklick auf das Floating-Icon zeigt oder versteckt das Hauptfenster.
- Rechtsklick auf das Floating-Icon oeffnet das Kontextmenue.
- Neue Stichpunkte werden unten im Eingabefeld zur ausgewaehlten Liste hinzugefuegt.
- Ein Doppelklick auf einen Stichpunkt oeffnet die Bearbeitung.
- Die Checkbox markiert Stichpunkte als offen oder erledigt.

Wichtige Tastaturkuerzel:

- `Ctrl+N`: Neue Liste
- `F2`: Liste umbenennen
- `Ctrl+Return`: Stichpunkt hinzufuegen
- `Ctrl+E`: Stichpunkt bearbeiten
- `Delete`: Auswahl loeschen
- `Esc`: Hauptfenster ausblenden

## Lokale Daten

Produktive Daten liegen unter:

```text
%APPDATA%\FloatNotes\
```

Wichtige Dateien:

- `notes.json`: Notizen und Aufgaben
- `settings.json`: lokale UI-Einstellungen
- `notes.backup-*.json`: automatische Backups

## Entwicklung

Voraussetzungen:

- Python 3.12+
- Windows

Setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

App starten:

```powershell
python -m app.main
```

Tests ausfuehren:

```powershell
python -m pytest
```

## Build

Windows-EXE bauen:

```powershell
.\tools\build_windows.ps1
```

Installer bauen:

```powershell
.\tools\build_installer.ps1
```

Build-Artefakte entstehen lokal in `build\`, `dist\` und `installer_output\`.

## Lizenz

FloatNotes steht unter der MIT-Lizenz. Details stehen in `LICENSE`.
