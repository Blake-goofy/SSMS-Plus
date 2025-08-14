# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Get the base Python installation directory (not the venv)
python_dir = sys.base_exec_prefix

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        # Explicitly include Python DLL from system Python installation
        (os.path.join(python_dir, 'python313.dll'), '.'),
    ],
    datas=[
        ('ssmsplus_yellow.ico', '.'),
        ('ssmsplus_red.ico', '.'),
    ],
    hiddenimports=['requests', 'pystray', 'PIL', 'PIL.Image'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SSMSPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ssmsplus_yellow.ico',
)
