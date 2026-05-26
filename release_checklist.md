# FloatNotes Release-Checkliste

## Vorbereitende Pruefung

PowerShell im Projektverzeichnis:

```powershell
.\tools\quality_check.ps1
```

## Build

PowerShell im Projektverzeichnis:

```powershell
.\.venv\Scripts\python.exe tools\create_icon.py
.\tools\build_windows.ps1
```

`FloatNotes.spec` ist das versionierte Build-Rezept. `build\` und `dist\` bleiben lokale Artefakte.

## Smoke-Test

- `dist\FloatNotes\FloatNotes.exe` starten.
- Floating-Icon anklicken und Hauptfenster oeffnen.
- Liste erstellen, Stichpunkt erstellen, abhaken, bearbeiten und loeschen.
- Rechtsklick-Menue am Floating-Icon pruefen.
- Datenpfad unter `%APPDATA%\FloatNotes` pruefen.
- Optionaler technischer Smoke-Test mit umgeleitetem `APPDATA`, damit keine produktiven Notizen beruehrt werden.

## Windows-Umgebungspruefungen

- Multi-Monitor: Floating-Icon auf jeden Monitor ziehen und pruefen, dass es innerhalb der sichtbaren Arbeitsflaeche bleibt.
- Multi-Monitor: App beenden und neu starten; gespeicherte Floating-Icon-Position pruefen.
- DPI-Skalierung: Hauptfenster und Floating-Icon bei 100 %, 125 % und 150 % Windows-Skalierung pruefen.
- DPI-Skalierung: Dialoge fuer Umbenennen und Loeschen auf abgeschnittene Texte oder zu kleine Buttons pruefen.
- Autostart: Nur bewusst ueber das Floating-Icon-Menue aktivieren, danach Neustart oder Ab-/Anmelden testen.
- Autostart: Deaktivieren im Floating-Icon-Menue pruefen und kontrollieren, dass die Verknuepfung entfernt wurde.

## Version und Artefakte

- Version in `pyproject.toml` pruefen.
- `.\.venv\Scripts\python.exe tools\sync_version.py` ausfuehren, damit `installer\FloatNotes.iss` synchron bleibt.
- Release-ZIP mit `.\tools\package_release.ps1` erzeugen, falls kein Installer ausgeliefert wird.
- `dist\FloatNotes` nicht direkt ausliefern; stattdessen `release_output\FloatNotes-<version>-win64.zip` oder den Installer verwenden.
- `build\`, `.venv\` und lokale Testdaten nicht ausliefern.

## Installer

Mit Inno Setup:

PowerShell im Projektverzeichnis:

```powershell
.\tools\build_installer.ps1
```

Erwartetes Artefakt: `installer_output\FloatNotesSetup.exe`.

## Installer-Smoke-Test

PowerShell im Projektverzeichnis:

```powershell
.\tools\smoke_test_installer.ps1
```

Pruefpunkte:

- Installation nach `.installer_smoke\FloatNotes`.
- Start der installierten `FloatNotes.exe`.
- Erstellung von `.installer_smoke\AppData\FloatNotes\notes.json`.
- Deinstallation ueber `unins000.exe`.
- Standardmodus: Keine echten Desktop-/Startmenue-Verknuepfungen im Smoke-Test, weil `/NOICONS` verwendet wird.
- Optionaler Desktop-Link-Test: `.\tools\smoke_test_installer.ps1 -CheckDesktopShortcut`.

## Signierung

Falls die App weitergegeben wird:

- Code-Signing-Zertifikat beschaffen.
- Windows SDK installieren oder `signtool.exe` in den PATH legen.
- PFX-Dateien niemals committen; `.gitignore` schliesst `*.pfx`, `*.p12` und `certs/` aus.
- EXE und Installer signieren:

```powershell
.\tools\sign_windows.ps1 -CertificatePath "C:\Pfad\zum\codesigning.pfx"
```

oder mit Zertifikat aus dem Windows-Zertifikatsspeicher:

```powershell
.\tools\sign_windows.ps1 -CertificateThumbprint "<SHA1-THUMBPRINT>"
```

- Signatur auf einer frischen Windows-Umgebung pruefen.

Ohne Signatur kann Windows SmartScreen Warnungen anzeigen.

## GitHub-Release

- Arbeitsbaum pruefen: `git status --short`.
- Alle gewollten Quell-, Test-, Doku- und Workflow-Dateien committen.
- Keine lokalen Artefaktordner committen: `build\`, `dist\`, `installer_output\`, `release_output\`, `.installer_smoke\`, `.venv\`.
- Release-Tag passend zur Version erstellen, z. B. `v0.1.0`.
- GitHub-Release mit kurzen Release Notes erstellen.
- Als Release-Artefakte hochladen:
  - `installer_output\FloatNotesSetup.exe`
  - optional `release_output\FloatNotes-<version>-win64.zip`
- Falls nicht signiert: Release Notes klar mit `Unsigned Windows build` kennzeichnen und SmartScreen-Warnung erwaehnen.
- Nach dem Upload Installer und ZIP einmal von GitHub herunterladen und auf einer frischen Windows-Umgebung testen.
