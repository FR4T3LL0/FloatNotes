# FloatNotes Development Log

## Phase 1 - Projektsetup

Datum: 2026-05-23

### Ziel

Das Projekt wurde als sauberes Python/PySide6-Grundgeruest im bestehenden Ordner `C:\Users\marco\dev\FloatNotes` angelegt.

### Erstellt

- `app/main.py`: Einstiegspunkt fuer die Desktop-App.
- `app/ui/main_window.py`: Minimal lauffaehiges Hauptfenster mit Sidebar und Inhaltsbereich.
- `app/ui/styles.py`: Erste moderne Qt-Stylesheet-Basis.
- `app/ui/floating_icon.py`: Platzhalter fuer das spaetere Floating-Icon.
- `app/core/app_paths.py`: Pfad-Helfer fuer spaetere Speicherung unter AppData.
- `data/example_notes.json`: Leere Beispielstruktur fuer spaetere JSON-Daten.
- `tests/test_project_structure.py`: Erster Strukturtest.
- `README.md`: Installations-, Start- und Strukturhinweise.
- `build_instructions.md`: Erste Build- und Autostart-Hinweise.
- `requirements.txt`: Projekt-Abhaengigkeiten.
- `pyproject.toml`: pytest-Konfiguration.
- `.gitignore`: Ignoriert virtuelle Umgebung, Python-Caches, Build-Ausgaben und interne Render-Artefakte.

### Entscheidung

PySide6 bleibt der Standard, weil es fuer eine native Windows-Desktop-App mit moderner Optik, Frameless-Fenstern, Always-on-top-Verhalten und spaeterem PyInstaller-Build gut passt. JSON reicht fuer die erste lokale, offline nutzbare Version aus.

### Testen

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
pytest
```

### Durchgefuehrte Checks

- `python --version`: Python 3.13.13 im aktuellen Terminal gefunden.
- `python -m compileall app tests`: erfolgreich.
- `python -c "from app.core.app_paths import get_notes_file_path; print(get_notes_file_path())"`: zeigt `C:\Users\marco\AppData\Roaming\FloatNotes\notes.json`.
- `python -m pytest`: noch nicht moeglich, weil `pytest` in der globalen Python-Installation nicht installiert ist. Nach `pip install -r requirements.txt` in der virtuellen Umgebung erneut ausfuehren.
- `python -c "import importlib.util; print(importlib.util.find_spec('PySide6') is not None)"`: aktuell `False`; PySide6 wird ueber `requirements.txt` installiert.

### Naechster sinnvoller Schritt

Phase 2: Datenmodell und robuste JSON-Speicherung mit automatischer Datei-Erstellung, Backup und Fehlerbehandlung.

## Phase 2 - Datenmodell und JSON-Speicherung

Datum: 2026-05-23

### Ziel

Die lokale Datenbasis fuer FloatNotes wurde implementiert. Die UI ist noch nicht angebunden; Phase 2 liefert die stabile Grundlage fuer spaetere CRUD-Funktionen.

### Erstellt/geaendert

- `app/core/models.py`: Dataclasses fuer `NoteItem`, `NoteList` und `NotesDocument`.
- `app/core/storage.py`: JSON-Storage mit automatischer Datei-Erstellung, atomarem Schreiben, Backup und Recovery bei kaputtem JSON.
- `app/core/__init__.py`: Core-Klassen als Paket-API exportiert.
- `tests/test_storage.py`: Tests fuer Erststart, Roundtrip, Backup und Corrupt-Recovery.
- `tests/test_project_structure.py`: Auf `unittest` umgestellt, damit Tests auch ohne installiertes `pytest` laufen.
- `README.md`: Speicherort, Backup-Verhalten und Testbefehle dokumentiert.

### Entscheidung

Die Datenmodelle bleiben bewusst schlank und verwenden `dataclasses` statt einer groesseren Validierungsbibliothek. Das passt zu einem lokalen Desktop-Tool und vermeidet unnoetige Abhaengigkeiten. Die produktiven Nutzdaten liegen spaeter unter `%APPDATA%\FloatNotes\notes.json`, nicht im Repository.

### Testen

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Nach Installation der Abhaengigkeiten in der virtuellen Umgebung:

```powershell
pytest
```

### Naechster sinnvoller Schritt

Phase 3: Hauptfenster an die Storage-Schicht anbinden, Listen aus JSON laden und die UI-Struktur fuer echte Daten vorbereiten.

## Phase 3 - Hauptfenster an Storage anbinden

Datum: 2026-05-23

### Ziel

Das Hauptfenster zeigt nun echte Daten aus der lokalen JSON-Datei an. Vollstaendige CRUD-Aktionen bleiben bewusst Phase 4, damit Anzeige, Auswahl und leere Zustaende zuerst stabil sind.

### Erstellt/geaendert

- `app/main.py`: Erstellt `NotesStorage`, laedt `NotesDocument` und uebergibt beides an das Hauptfenster.
- `app/ui/main_window.py`: Rendert Listen aus dem Dokument, zeigt Stichpunkte der ausgewaehlten Liste und behandelt leere Zustaende.
- `app/ui/styles.py`: Styles fuer Sidebar-Auswahl, Stichpunkt-Karten, Empty-State und Statusleiste ergaenzt.
- `data/example_notes.json`: Beispielinhalt mit zwei Listen und Stichpunkten ergaenzt.
- `tests/test_models.py`: Tests fuer Sortierung, Listenauswahl und `done`-Kompatibilitaet ergaenzt.
- `README.md`: Startverhalten und Beispiel-JSON dokumentiert.

### Entscheidung

Das Hauptfenster bekommt Storage und Dokument injiziert, statt selbst Dateizugriffe zu verstecken. Das trennt UI und Speicherlogik und macht Phase 4 einfacher, weil CRUD-Aktionen spaeter nur das Dokument aendern und anschliessend speichern muessen.

### Testen

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Nach Installation der Abhaengigkeiten:

```powershell
python -m app.main
```

### Naechster sinnvoller Schritt

Phase 4: CRUD-Funktionen fuer Listen und Stichpunkte aktivieren und automatische Speicherung nach jeder Aenderung anbinden.

## Phase 4 - CRUD-Funktionen und Auto-Save

Datum: 2026-05-23

### Ziel

Die App kann nun Listen und Stichpunkte direkt im Hauptfenster erstellen, bearbeiten, loeschen und speichern. Jede Aenderung wird sofort ueber `NotesStorage` in die lokale JSON-Datei geschrieben.

### Erstellt/geaendert

- `app/ui/main_window.py`: Listen-CRUD, Stichpunkt-CRUD, Checkbox fuer erledigte Stichpunkte, Dialoge und Speicherfehlerbehandlung implementiert.
- `app/ui/styles.py`: Sekundaere und destruktive Button-Styles ergaenzt.
- `app/core/models.py`: Reihenfolge der Items wird nach Loeschen normalisiert und intern stabil sortiert.
- `tests/test_models.py`: Tests fuer Listen- und Stichpunkt-CRUD, Reihenfolge und Validierung ergaenzt.
- `README.md`: Aktuelle Funktionen und Bedienung dokumentiert.

### Entscheidung

CRUD bleibt in der UI bewusst schlank: einfache Eingabedialoge, klare Loesch-Bestaetigungen und sofortiges Speichern nach jeder erfolgreichen Aenderung. Die eigentlichen Datenoperationen bleiben in den Modellen; die UI koordiniert Auswahl, Dialoge und Auto-Save.

### Testen

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Nach Installation der Abhaengigkeiten:

```powershell
python -m app.main
```

### Durchgefuehrte Checks

- `python -m compileall app tests`: erfolgreich.
- `python -m unittest discover -s tests`: 11 Tests erfolgreich.
- ASCII-Check fuer Projektdateien: keine nicht-ASCII-Zeichen gefunden.

### Naechster sinnvoller Schritt

Phase 5: Floating-Icon als kleines transparentes Always-on-top-Fenster bauen, das das Hauptfenster ein- und ausblendet und per Drag verschoben werden kann.

## Phase 5 - Floating-Icon

Datum: 2026-05-23

### Ziel

FloatNotes startet jetzt ueber ein kleines dauerhaft sichtbares Floating-Icon. Das Icon liegt im Vordergrund, ist halbtransparent, kann verschoben werden und zeigt oder versteckt per Klick das Hauptfenster.

### Erstellt/geaendert

- `app/ui/floating_icon.py`: Echtes frameless Always-on-top-Fenster mit Transparenz, Drag, Klick-Toggle und Rechtsklick-Menue.
- `app/main.py`: Startet nun Floating-Icon und Hauptfenster gemeinsam; das Hauptfenster bleibt initial verborgen.
- `app/core/settings.py`: Lokale UI-Settings fuer die Floating-Icon-Position.
- `app/core/app_paths.py`: Pfad fuer `settings.json` ergaenzt.
- `app/core/__init__.py`: Settings-Klassen exportiert.
- `tests/test_settings.py`: Tests fuer Default-Settings, Roundtrip und Recovery kaputter Settings.
- `tests/test_project_structure.py`: Settings-Pfadtest ergaenzt.
- `README.md`: Floating-Icon-Bedienung und Settings-Datei dokumentiert.

### Entscheidung

Das Floating-Icon ist ein separates `QWidget` mit `FramelessWindowHint`, `WindowStaysOnTopHint` und transparenter Hintergrundflaeche. Die Position wird nur beim Draggen gespeichert. Autostart oder andere Windows-Systemaenderungen werden nicht aktiviert.

### Testen

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Nach Installation der Abhaengigkeiten:

```powershell
python -m app.main
```

Manueller UI-Test:

- Beim Start erscheint nur das Floating-Icon.
- Linksklick zeigt oder versteckt das Hauptfenster.
- Ziehen mit linker Maustaste verschiebt das Icon.
- Rechtsklick zeigt Oeffnen/Ausblenden und Beenden.

### Naechster sinnvoller Schritt

Phase 6: Design-Polish fuer Hauptfenster und Floating-Icon, inklusive feineren Abstaenden, visueller Hierarchie, Schattenwirkung und konsistenterem Apple-inspiriertem Look.

## Phase 6 - Design-Polish

Datum: 2026-05-23

### Ziel

Die bestehende Funktionalitaet wurde optisch verfeinert. Fokus: hochwertigeres Hauptfenster, klarere visuelle Hierarchie, weichere Flaechen, bessere Hover-/Focus-Zustaende und ein moderneres Floating-Icon.

### Erstellt/geaendert

- `app/ui/widgets.py`: Wiederverwendbarer Helfer fuer weiche Qt-Schatten.
- `app/ui/main_window.py`: Panel-Schatten, Header-Zeile, Status-Badge, Input-Bar und bessere Empty-State-Texte ergaenzt.
- `app/ui/styles.py`: Farbpalette, Button-States, Listen-States, Fokusrahmen, Menue-Styles und Scrollbar-Styles verfeinert.
- `app/ui/floating_icon.py`: Icon-Zeichnung mit Glasflaeche, weichem Schatten und Notiz-Symbol statt Textplatzhalter ueberarbeitet.
- `README.md`: Design-Stand und Projektstruktur aktualisiert.

### Entscheidung

Der Polish bleibt bewusst im bestehenden PySide6-Stack. Schatten werden mit `QGraphicsDropShadowEffect` umgesetzt, das Floating-Icon wird direkt mit `QPainter` gezeichnet. Dadurch entstehen keine neuen externen Abhaengigkeiten und der spaetere PyInstaller-Build bleibt ueberschaubar.

### Testen

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Nach Installation der Abhaengigkeiten:

```powershell
python -m app.main
```

Manueller UI-Test:

- Hauptfenster ueber Floating-Icon oeffnen.
- Sidebar-Auswahl, Button-Hover, Input-Fokus und Empty-State pruefen.
- Stichpunkte erstellen, bearbeiten, abhaken und loeschen.
- Floating-Icon verschieben, ausblenden/einblenden und per Rechtsklick-Menue beenden.

### Durchgefuehrte Checks

- `python -m compileall app tests`: erfolgreich.
- `python -m unittest discover -s tests`: 15 Tests erfolgreich.
- ASCII-Check fuer Projektdateien: keine nicht-ASCII-Zeichen gefunden.
- `PySide6` ist in der globalen Python-Installation aktuell nicht installiert; manueller UI-Start erfolgt nach `pip install -r requirements.txt`.

### Naechster sinnvoller Schritt

Phase 7: Dokumentation finalisieren und die bisherigen Entwicklungs-, Start-, Test- und Bedienhinweise konsolidieren.

## Phase 7 - Dokumentation konsolidieren

Datum: 2026-05-23

### Ziel

Die Dokumentation wurde auf den aktuellen Projektstand gebracht. README und Build-Anleitung sind nun als praktische Referenzen nutzbar, ohne dass der Chatverlauf gelesen werden muss.

### Erstellt/geaendert

- `README.md`: Neu strukturiert mit Status, Installation, Start, Bedienung, Tests, Datenpfaden, Projektstruktur, Architektur, Design-Stand, EXE-Build und Autostart-Hinweisen.
- `build_instructions.md`: Neu strukturiert mit Voraussetzungen, Entwicklungsstart, Tests, vorbereitetem PyInstaller-Befehl, Datenpfaden im EXE-Betrieb, Bereinigungshinweisen und Autostart-Konzept.
- `DEVELOPMENT_LOG.md`: Phase-7-Eintrag ergaenzt.
- `FloatNotes Doku.docx`: Phase-7-Eintrag wird parallel gepflegt.

### Entscheidung

Die Dokumentation wurde konsolidiert statt weiter nur erweitert. Dadurch bleiben die wichtigsten Informationen oben in den jeweiligen Dateien klar auffindbar. Der finale EXE-Build bleibt bewusst Phase 8, aber der voraussichtliche PyInstaller-Befehl und die erwarteten Artefakte sind bereits dokumentiert.

### Testen

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m unittest discover -s tests
python -m compileall app tests
```

Nach Installation der Abhaengigkeiten:

```powershell
python -m app.main
```

### Naechster sinnvoller Schritt

Phase 8: PyInstaller-Build als Windows-EXE ausfuehren, Build-Artefakte pruefen und Build-Anleitung finalisieren.

## Phase 8 - Build als Windows-EXE

Datum: 2026-05-23

### Ziel

Die App wurde mit PyInstaller als Windows-Desktop-Anwendung gebaut und der Build wurde mit Tests, Artefaktpruefung und Smoke-Test validiert.

### Erstellt/geaendert

- `.venv/`: Virtuelle Umgebung im Projektordner erstellt.
- `build/`: PyInstaller-Arbeitsverzeichnis erzeugt.
- `dist/FloatNotes/FloatNotes.exe`: Ausfuehrbare Windows-App erzeugt.
- `FloatNotes.spec`: PyInstaller-Spec-Datei erzeugt.
- `README.md`: Build-Status auf Phase 8 aktualisiert.
- `build_instructions.md`: Tatsaechlichen PyInstaller-Befehl, Artefakte, Groessen und Smoke-Test dokumentiert.
- `DEVELOPMENT_LOG.md`: Phase-8-Eintrag ergaenzt.
- `FloatNotes Doku.docx`: Phase-8-Eintrag wird parallel gepflegt.

### Entscheidung

Der Build nutzt `--windowed`, damit beim Start keine Konsole erscheint, und `--paths .`, damit die Paketimporte aus `app/` sauber aufgeloest werden. Es wurde kein Icon eingebunden; ein eigenes Windows-App-Icon kann spaeter als eigener Asset-Schritt folgen.

### Durchgefuehrte Befehle

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m compileall app tests
.\.venv\Scripts\pyinstaller.exe --noconfirm --windowed --name FloatNotes --paths . app\main.py
```

### Ergebnis

- PySide6 6.11.1 installiert.
- PyInstaller 6.20.0 installiert.
- `pytest`: 15 Tests erfolgreich.
- `compileall`: erfolgreich.
- EXE erzeugt: `dist\FloatNotes\FloatNotes.exe`.
- EXE-Groesse: ca. 1.8 MB.
- Gesamtgroesse `dist\FloatNotes`: ca. 116 MB.
- Smoke-Test: EXE startete, blieb lauffaehig und erstellte `notes.json` unter einem umgeleiteten Test-`APPDATA`.

### Hinweise

PyInstaller meldete fehlende optionale Module wie `pwd`, `grp`, `fcntl`, `posix` und `java`. Diese stammen aus plattformabhaengigen optionalen Imports und sind fuer die Windows-App nicht relevant.

### Naechster sinnvoller Schritt

Phase 9: Optionalen Windows-Autostart vorbereiten und dokumentieren, ohne ihn automatisch zu aktivieren.

## Phase 9 - Optionaler Windows-Autostart

Datum: 2026-05-23

### Ziel

Autostart wurde als bewusst aktivierbare Windows-Funktion vorbereitet. Die App aktiviert Autostart nicht automatisch; eine Aenderung erfolgt nur nach Rechtsklick auf das Floating-Icon und Bestaetigung durch den Benutzer.

### Erstellt/geaendert

- `app/core/autostart.py`: Current-User-Autostart ueber `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` vorbereitet.
- `app/core/__init__.py`: Autostart-Klassen und Funktionen exportiert.
- `app/ui/floating_icon.py`: Rechtsklick-Menue um `Autostart aktivieren/deaktivieren` mit Bestaetigungsdialog erweitert.
- `tests/test_autostart.py`: Tests fuer Command-Quoting, EXE-Zielerkennung und Support-Erkennung.
- `README.md`: Autostart-Bedienung und Registry-Wert dokumentiert.
- `build_instructions.md`: Autostart-Statuscheck, manuelles Entfernen und Startup-Ordner-Alternative dokumentiert.
- `DEVELOPMENT_LOG.md`: Phase-9-Eintrag ergaenzt.
- `FloatNotes Doku.docx`: Phase-9-Eintrag wird parallel gepflegt.

### Entscheidung

Die Implementierung nutzt den Windows Current-User-Run-Key statt Administratorrechte oder globaler Systempfade. Das ist fuer eine persoenliche Desktop-App angemessen, bleibt pro Benutzer begrenzt und kann ohne Adminrechte entfernt werden. Bei Source-Starts wird nicht versehentlich `python.exe` fuer Autostart verwendet; die Funktion erwartet den gebauten EXE-Pfad.

### Durchgefuehrte Checks

- `.\.venv\Scripts\python.exe -m compileall app tests`: erfolgreich.
- `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider`: 19 Tests erfolgreich.
- PyInstaller-Build nach UI-Aenderung erneut ausgefuehrt.
- EXE-Smoke-Test: Prozess startete, blieb lauffaehig und legte `notes.json` unter umgeleitetem Test-`APPDATA` an.
- Autostart wurde nicht aktiviert und kein Registry-Wert wurde durch die Tests geschrieben.

### Ergebnis

- Neue EXE: `dist\FloatNotes\FloatNotes.exe`.
- EXE-Groesse: ca. 1.8 MB.
- Gesamtgroesse `dist\FloatNotes`: ca. 116 MB.

### Naechster sinnvoller Schritt

Projektabschluss pruefen oder optional ein eigenes App-Icon/Installer-Paket als naechste Ausbaustufe planen.

## Nacharbeit - Floating-Icon Verhalten und Micro-Interactions

Datum: 2026-05-23

### Ziel

Das Floating-Icon soll sich hochwertiger anfuehlen und nicht mehr ueber den sichtbaren Desktop hinaus verschoben werden koennen.

### Erstellt/geaendert

- `app/ui/geometry.py`: Testbare Clamp-Funktion fuer Fensterpositionen innerhalb der verfuegbaren Bildschirmflaeche.
- `app/ui/floating_icon.py`: Drag-Bewegung wird auf die aktuelle Bildschirmflaeche begrenzt; gespeicherte Positionen werden beim Start ebenfalls korrigiert.
- `app/ui/floating_icon.py`: Dezente Hover- und Drag-Opacity-Animationen sowie leichte visuelle Hover-Akzente ergaenzt.
- `tests/test_geometry.py`: Tests fuer negative Positionen, rechte/untere Kanten, versetzte Bildschirme und sehr kleine Flaechen.
- `README.md`: Bedienung, Projektstruktur und Architektur aktualisiert.
- `dist/FloatNotes/FloatNotes.exe`: Nach der Icon-Aenderung neu gebaut.

### Entscheidung

Die Bildschirmbegrenzung wurde als pure Hilfsfunktion umgesetzt, damit das Verhalten ohne GUI-Test reproduzierbar pruefbar bleibt. Die eigentliche PySide6-Integration nutzt die verfuegbare Screen-Geometrie, sodass Taskleistenbereiche beruecksichtigt werden.

### Durchgefuehrte Checks

- `.\.venv\Scripts\python.exe -m compileall app tests`: erfolgreich.
- `.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider`: 23 Tests erfolgreich.
- PyInstaller-Build nach Aenderung: erfolgreich.
- EXE-Smoke-Test: Prozess startete und blieb lauffaehig.

### Weitere Premium-Ideen

- Kurze Fade-Animation beim Ein- und Ausblenden des Hauptfensters.
- Edge-Snap mit dezenter Magnetwirkung an Bildschirmraendern.
- Minimale Toast-Meldung nach Speichern statt Statusleisten-Text.
- Tastaturkurzbefehle fuer neue Liste, neuer Stichpunkt und schnelles Ein-/Ausblenden.
- Eigenes App-Icon und Installer-Paket fuer einen runderen Windows-Eindruck.

## Optimierungsrunde - Release-Qualitaet und Premium-Verhalten

Datum: 2026-05-24

### Ziel

Die Punkte aus `optimierungsvorschlaege.txt` wurden geprueft und umgesetzt, soweit sie ohne riskante Systemaenderungen moeglich sind. Der Fokus lag auf nachvollziehbarem Build, kleinerem PyInstaller-Paket, App-Icon, Tray-Integration, robusterer Speicherung, Tests und Release-Dokumentation.

### Erstellt/geaendert

- `.gitignore`: `FloatNotes.spec` wird bewusst versioniert, waehrend `build\` und `dist\` lokale Artefakte bleiben.
- `FloatNotes.spec`: Icon, Add-Data, Modul-Excludes sowie Filter fuer ungenutzte Qt-Plugins und Qt-Translations.
- `tools\build_windows.ps1`: Baut ueber `FloatNotes.spec` und erzeugt das Icon bei Bedarf neu.
- `tools\quality_check.ps1`: Einheitlicher Quality-Gate-Befehl mit Ruff-Lint, Ruff-Formatcheck, Pytest und Compileall.
- `tools\create_icon.py`: Erzeugt `app\assets\floatnotes.ico`.
- `app\assets\floatnotes.ico`: Eigenes App-/EXE-Icon.
- `app\ui\app_icon.py`: Icon-Pfad fuer Source- und PyInstaller-Betrieb.
- `app\ui\tray_icon.py`: System-Tray-Icon mit Oeffnen, Ausblenden, Floating-Icon anzeigen und Beenden; Kontextmenue wird als Attribut gehalten, damit PySide es nicht vorzeitig freigibt.
- `app\main.py`: App-Icon und Tray-Controller eingebunden.
- `app\ui\main_window.py`: Debounced Auto-Save und Tastaturkuerzel.
- `app\core\storage.py`: Zeitgestempelte Backup-Dateien und Rotation der letzten 5 Backups.
- `app\core\settings.py`: Zeitgestempelte Recovery-Dateien fuer beschaedigte Settings.
- `tests\test_storage.py`: Backup-Rotation abgedeckt.
- `tests\test_settings.py`: Settings-Recovery mit Zeitstempel abgedeckt.
- `tests\test_autostart.py`: Enable/Disable-Autostart mit gemocktem `winreg`.
- `tests\test_ui_smoke.py`: UI-Smoke-Test fuer Hauptfenster und Floating-Icon.
- `installer\FloatNotes.iss`: Inno-Setup-Vorlage vorbereitet.
- `release_checklist.md`: Release-Prozess mit Tests, Build, Smoke-Test, Installer und Signierung.
- `README.md` und `build_instructions.md`: Dokumentation auf den optimierten Stand gebracht.
- `FloatNotes Doku.docx`: Optimierungsrunde mit Dateien, Wirkung, Tests und naechstem Schritt ergaenzt.

### Entscheidung

`FloatNotes.spec` ist jetzt die Build-Quelle, weil Icon, Daten, Excludes und Plugin-/Translation-Filter dort reproduzierbar beschrieben sind. Echte EXE-Signierung und ein gebauter Installer wurden bewusst nicht automatisiert, weil dafuer lokale Werkzeuge beziehungsweise ein Zertifikat noetig sind. Autostart bleibt vorbereitet, wird aber nicht ohne Benutzerbestaetigung aktiviert.

### Durchgefuehrte Checks

Terminal: PyCharm Terminal  
Pfad: `C:\Users\marco\dev\FloatNotes`

```powershell
.\tools\quality_check.ps1
.\tools\build_windows.ps1
```

Ergebnisse:

- Ruff-Lint erfolgreich.
- Ruff-Formatcheck erfolgreich.
- Pytest: 26 Tests erfolgreich.
- Compileall erfolgreich.
- EXE neu gebaut: `dist\FloatNotes\FloatNotes.exe`.
- EXE-Groesse: ca. 1.8 MB.
- Gesamtgroesse `dist\FloatNotes`: ca. 86.6 MB.
- Qt-Translations entfernt; im Plugin-Ordner bleiben nur `qwindows`, `qico` und `qmodernwindowsstyle`.
- `FloatNotes Doku.docx` strukturell mit `python-docx` gelesen und geprueft.
- Visuelle DOCX-Renderpruefung nicht moeglich, weil `soffice`/LibreOffice nicht gefunden wurde.

Erwarteter technischer Smoke-Test:

```powershell
$env:APPDATA = 'C:\Users\marco\dev\FloatNotes\.smoke_appdata'
dist\FloatNotes\FloatNotes.exe
```

Ergebnis: Prozess startete, blieb lauffaehig und erzeugte `.smoke_appdata\FloatNotes\notes.json`.

### Naechster sinnvoller Schritt

Einen echten Release nur dann erstellen, wenn die App weitergegeben werden soll: Inno Setup lokal installieren, Installer aus `installer\FloatNotes.iss` bauen und optional mit einem Code-Signing-Zertifikat signieren.

## UI-Textanpassung - Deutsche Umlaute

Datum: 2026-05-24

### Ziel

Sichtbare UI-Texte wurden von ASCII-Umschreibungen wie `Oeffnen`, `Loeschen`, `Hinzufuegen` und `Beschaedigte` auf echte deutsche Umlaute umgestellt.

### Erstellt/geaendert

- `app\main.py`: Startup-Hinweis fuer beschaedigte JSON auf `Beschädigte JSON gesichert` angepasst.
- `app\ui\floating_icon.py`: Tooltip, Kontextmenue und Autostart-Dialoge mit `öffnen`, `verfügbar` und `ausführen`.
- `app\ui\tray_icon.py`: Tray-Menuepunkt `Öffnen`.
- `app\ui\main_window.py`: Buttons, Dialogtitel, Bestaetigungstexte und Empty-State-Texte mit `Löschen`, `Hinzufügen`, `ausgewählt`, `Füge` und `gelöscht`.
- `FloatNotes Doku.docx`: Diese UI-Textanpassung dokumentiert.

### Wirkung der Aenderung

Die App wirkt in der deutschen Oberfläche nativer und hochwertiger, ohne technische Dateinamen, Pfade oder interne englische Fehlermeldungen zu verändern.

### Durchgefuehrte Checks

- `.\tools\quality_check.ps1`: erfolgreich.
- Pytest: 26 Tests erfolgreich.
- PyInstaller-Build ueber `.\tools\build_windows.ps1`: erfolgreich.
- EXE-Smoke-Test mit umgeleitetem `APPDATA`: Prozess startete und blieb lauffaehig.

### Naechster sinnvoller Schritt

Optional kann spaeter eine zentrale Datei fuer alle UI-Texte eingefuehrt werden, falls Internationalisierung oder ein systematisches Wording gewuenscht ist.

## UI-Update nach Optimierungs-Vorlagen

Datum: 2026-05-24

### Ziel

Die beiden Vorlagen im Ordner `Bilder` wurden umgesetzt: `UI Update.png` als visuelle Referenz und `UI Update.txt` als konkrete Aufgabenliste.

### Erstellt/geaendert

- `app\ui\main_window.py`: Sidebar-Listeneintraege als eigene Zeilen mit Akzentbalken, Icon-Platzhalter und Zaehl-Badge aufgebaut.
- `app\ui\main_window.py`: Eingabebereich aus dem Body geloest und als klarer Footer des Content-Panels gestaltet.
- `app\ui\main_window.py`: Bearbeiten-/Loeschen-Aktionen fuer Stichpunkte werden nur noch angezeigt, wenn wirklich ein Stichpunkt ausgewaehlt ist.
- `app\ui\main_window.py`: `0 offen` wird bei komplett erledigten Listen durch `✓ Alles erledigt` ersetzt.
- `app\ui\main_window.py`: Aufgabenliste setzt kleinere, ruhigere Listeneintraege und zeigt ohne Auswahl den Hinweis `Keine Aufgabe ausgewählt`.
- `app\ui\styles.py`: Styles fuer aktive Listenzeilen, Akzentbalken, Zaehl-Badges, Footer, Selection-Hint und ruhigere Aufgaben-Karten ergaenzt.
- `tests\test_ui_smoke.py`: UI-Smoke-Test fuer `Alles erledigt` und versteckte Stichpunkt-Aktionen ergaenzt.
- `tools\quality_check.ps1`: Native Exitcodes werden jetzt geprueft, damit das Quality Gate bei Ruff-/Testfehlern wirklich abbricht.
- `README.md`: Design-Stand mit den neuen UI-Regeln aktualisiert.
- `FloatNotes Doku.docx`: UI-Update dokumentiert.

### Wirkung der Aenderung

Die Hauptoberflaeche folgt staerker der Referenz: Die aktive Liste ist klarer erkennbar, der Footer wirkt strukturierter, nicht relevante Aktionen verschwinden, und abgeschlossene Listen bekommen ein positives Status-Badge statt `0 offen`.

### Durchgefuehrte Checks

- `.\tools\quality_check.ps1`: erfolgreich.
- Pytest: 27 Tests erfolgreich.
- PyInstaller-Build ueber `.\tools\build_windows.ps1`: erfolgreich.
- EXE-Smoke-Test mit umgeleitetem `APPDATA`: Prozess startete und blieb lauffaehig.

### Naechster sinnvoller Schritt

Optional koennen die Aufgaben-Zeilen spaeter komplett als eigene Widgets gebaut werden, wenn Checkboxen, Check-Kreis und Item-Hover noch naeher an die visuelle Vorlage ruecken sollen.
