# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


base = Path(SPECPATH)
native_bin = base / "dectalk" / "native_bin"
datas = []
if native_bin.exists():
    datas.append((str(native_bin), "dectalk/native_bin"))

a = Analysis(
    [str(base / "dectalk" / "__main__.py")],
    pathex=[str(base)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name="dectalk-python",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
