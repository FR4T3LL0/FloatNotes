# FloatNotes Release-Checkliste

## Vorbereitende Pruefung

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
.\tools\quality_check.ps1
```

## Build

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

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

## Version und Artefakte

- Version in `pyproject.toml` pruefen.
- `.\.venv\Scripts\python.exe tools\sync_version.py` ausfuehren, damit `installer\FloatNotes.iss` synchron bleibt.
- `dist\FloatNotes` als ZIP oder Installer ausliefern.
- `build\`, `.venv\` und lokale Testdaten nicht ausliefern.

## Installer

Optional mit Inno Setup:

Terminal: Inno Setup Compiler  
Pfad: `C:\Users\marco\dev\FloatNotes`

```text
installer\FloatNotes.iss
```

Der Installer wird erst gebaut, wenn Inno Setup lokal installiert ist.

## Signierung

Falls die App weitergegeben wird:

- Code-Signing-Zertifikat beschaffen.
- EXE oder Installer mit `signtool.exe` signieren.
- Signatur auf einer frischen Windows-Umgebung pruefen.

Ohne Signatur kann Windows SmartScreen Warnungen anzeigen.
