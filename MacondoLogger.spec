# -*- mode: python ; coding: utf-8 -*-
# Macondo Logger (Bug Logger only).
# Build:  build_all.bat   (or: python -m PyInstaller MacondoLogger.spec --noconfirm)
# Result: dist\MacondoLogger.exe
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules, copy_metadata

# The app's .py files. Streamlit loads them at run time (PyInstaller's static
# analysis doesn't see them), so they have to be bundled as data
# so they stay together and can import each other.
APP_FILES = [
    "launcher_macondo.py",
    "macondo_app.py",
    "bug_logger_ui.py",
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

# groq brings code that streamlit doesn't pull in on its own: we collect all of it.
for pkg in ("groq",):
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

# keyring discovers its Windows backend (Credential Manager) at run time:
# it has to be bundled in full or the .exe fails with "No module named keyring".
for pkg in ("keyring", "jaraco.classes", "jaraco.functools", "jaraco.context", "win32ctypes"):
    try:
        d, b, h = collect_all(pkg)
        datas += d; binaries += b; hiddenimports += h
    except Exception:
        pass
hiddenimports += collect_submodules("keyring.backends")

a = Analysis(
    ["launcher_macondo.py"],
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
    name="MacondoLogger",
    console=False,  # no black console window
    upx=False,
)
