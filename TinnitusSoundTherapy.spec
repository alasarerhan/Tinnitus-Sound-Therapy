# -*- mode: python ; coding: utf-8 -*-

import os
OUTPATH = os.path.join(os.path.expanduser('~'), 'Desktop')  # This will put it on your Desktop

block_cipher = None

a = Analysis(
    ['frequency_generator.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['scipy', 'scipy.signal'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorflow', 'keras', 'torch', 'PIL', 'matplotlib'],
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
    name='TinnitusNoiseGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
    windowed=True,
    distpath=OUTPATH  # This line specifies where to put the executable
)
