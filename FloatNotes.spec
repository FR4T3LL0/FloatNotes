# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('app\\assets\\floatnotes.ico', 'app\\assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtDesigner', 'PySide6.QtSql', 'PySide6.QtBluetooth', 'PySide6.QtMultimedia', 'PySide6.QtOpenGL', 'PySide6.QtPdf', 'PySide6.QtPrintSupport', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets'],
    noarchive=False,
    optimize=0,
)

# Keep the Windows build smaller by dropping Qt pieces that FloatNotes does not use.
# The app needs widgets, the Windows platform plugin, ICO loading and the Windows style.
excluded_qt_parts = (
    'PySide6\\translations',
    'PySide6\\plugins\\generic\\',
    'PySide6\\plugins\\iconengines\\',
    'PySide6\\plugins\\networkinformation\\',
    'PySide6\\plugins\\platforminputcontexts\\',
    'PySide6\\plugins\\tls\\',
    'PySide6\\plugins\\platforms\\qdirect2d.dll',
    'PySide6\\plugins\\platforms\\qminimal.dll',
    'PySide6\\plugins\\platforms\\qoffscreen.dll',
    'PySide6\\plugins\\imageformats\\qgif.dll',
    'PySide6\\plugins\\imageformats\\qicns.dll',
    'PySide6\\plugins\\imageformats\\qjpeg.dll',
    'PySide6\\plugins\\imageformats\\qpdf.dll',
    'PySide6\\plugins\\imageformats\\qsvg.dll',
    'PySide6\\plugins\\imageformats\\qtga.dll',
    'PySide6\\plugins\\imageformats\\qtiff.dll',
    'PySide6\\plugins\\imageformats\\qwbmp.dll',
    'PySide6\\plugins\\imageformats\\qwebp.dll',
    'PySide6\\Qt6Pdf.dll',
    'PySide6\\Qt6Qml.dll',
    'PySide6\\Qt6QmlMeta.dll',
    'PySide6\\Qt6QmlModels.dll',
    'PySide6\\Qt6QmlWorkerScript.dll',
    'PySide6\\Qt6Quick.dll',
    'PySide6\\Qt6Svg.dll',
    'PySide6\\Qt6VirtualKeyboard.dll',
)


def keep_toc_entry(entry):
    name = entry[0].replace('/', '\\')
    return not any(part in name for part in excluded_qt_parts)


a.datas = [data for data in a.datas if keep_toc_entry(data)]
a.binaries = [binary for binary in a.binaries if keep_toc_entry(binary)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FloatNotes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app\\assets\\floatnotes.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FloatNotes',
)
