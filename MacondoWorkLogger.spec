# -*- mode: python ; coding: utf-8 -*-
# Macondo WorkLogger (time logging only).
# Build:  build_all.bat   (or: python -m PyInstaller MacondoWorkLogger.spec --noconfirm)
# Result: dist\MacondoWorkLogger.exe
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules, copy_metadata

APP_FILES = [
    "launcher_worklogger.py",
    "worklogger_app.py",
    "worklogger_ui.py",
    "worklogger_core.py",
    "core.py",
    "macondo_theme.py",
    "macondo_login.py",
    "_launcher_base.py",
    "macondo_logo.jpg",
]

datas = [(f, ".") for f in APP_FILES]
binaries = []
hiddenimports = [
    "streamlit.web.cli",
    "streamlit.runtime.scriptrunner.magic_funcs",
    "groq", "requests", "keyring",
]

datas += collect_data_files("streamlit")
for pkg in ("streamlit", "groq", "requests", "keyring"):
    datas += copy_metadata(pkg)

# The WorkLogger doesn't use AI, but core.py imports groq when it loads, so the
# package has to be included anyway (otherwise importing core fails).
for pkg in ("groq",):
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

for pkg in ("keyring", "jaraco.classes", "jaraco.functools", "jaraco.context", "win32ctypes"):
    try:
        d, b, h = collect_all(pkg)
        datas += d; binaries += b; hiddenimports += h
    except Exception:
        pass
hiddenimports += collect_submodules("keyring.backends")

a = Analysis(
    ["launcher_worklogger.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "matplotlib", "IPython"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="MacondoWorkLogger",
    console=False,
    upx=False,
)
