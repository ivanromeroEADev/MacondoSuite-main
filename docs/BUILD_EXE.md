# Building the Macondo executables

This folder produces three independent `.exe` files from the same code:

| Executable | What it does |
|---|---|
| `MacondoLogger.exe` | Only the **Bug Logger** (log bugs in JaaS with AI). |
| `MacondoWorkLogger.exe` | Only the **WorkLogger** (log hours in JaaS). |
| `MacondoSuite.exe` | **Both**, in tabs, with a single connection. |

All three share the same core (`core.py`, `worklogger_core.py`), so a
fix in the logic works for all of them.

## Requirements (once per PC)

1. **Python 3.11 or newer** from [python.org](https://www.python.org/downloads/).
   When installing, check **"Add python.exe to PATH"**.
2. Nothing else: the `.bat` files install the dependencies on their own.

> Building **only works on Windows**. The `.exe` is generated on your PC;
> what's delivered here is the source code and the instructions.

## Build

Double-click the `.bat` you need:

- **`build_all.bat`** → builds all three `.exe` files.
- `build_macondo.bat` → only `MacondoLogger.exe`.
- `build_worklogger.bat` → only `MacondoWorkLogger.exe`.
- `build_suite.bat` → only `MacondoSuite.exe`.

The executables end up in the **`dist\`** folder. It takes a few minutes the first time.

If you prefer the command line:

```cmd
python -m pip install -r requirements.txt pyinstaller
python -m PyInstaller MacondoSuite.spec --noconfirm
```

## Try it without building (development mode)

To see the app before generating the `.exe`:

```cmd
python -m pip install -r requirements.txt
python -m streamlit run macondo_suite_app.py
```

(or `macondo_app.py` / `worklogger_app.py` for the standalone versions).

## First launch of an `.exe`

1. When you open it, a local server starts and the browser opens on its own.
2. **Bug Logger / Suite:** the first time, it asks for the **Groq API Key** (it's stored
   encrypted on this computer, you don't have to paste it again).
3. It asks for the **JaaS PAT Token** once (also stored encrypted with the
   Windows Credential Manager).

## If something fails

- **"Python not found"** → install it checking *Add to PATH* and reopen the `.bat`.
- **`pyinstaller` not recognized** → use `python -m PyInstaller ...` (the `.bat` files already do).
- **"No module named keyring" when opening the `.exe`** → delete the `build\` folder and
  rebuild; the `.spec` already includes keyring and its Windows backend.
- **Windows SmartScreen / Defender blocks the `.exe`** → that's normal for an `.exe`
  without a digital signature. *More info → Run anyway*. For wide
  distribution it's worth signing it (see [the distribution brief](briefs/00_Overview_and_Distribution.md)).
