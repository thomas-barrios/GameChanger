# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Use the current working directory as the project root
PROJ_ROOT = Path(os.getcwd())
SRC_DIR = PROJ_ROOT / 'src'
ASSETS_DIR = PROJ_ROOT / 'assets'
DIST_DIR = PROJ_ROOT / 'dist'

block_cipher = None

a = Analysis(
    [str(SRC_DIR / 'game_changer.py')],  # Correct path to game_changer.py
    pathex=[str(SRC_DIR)],
    binaries=[],
    datas=[
        (str(SRC_DIR / '*.py'), '.'),      # Include all Python files
        (str(PROJ_ROOT / 'README.md'), '.'),
        (str(PROJ_ROOT / 'LICENSE'), '.'),
        (str(ASSETS_DIR / 'icon.ico'), '.')
    ],
    hiddenimports=['win32com.client', 'win32timezone'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GameChanger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ASSETS_DIR / 'icon.ico'),
    version='file_version_info.txt'
)