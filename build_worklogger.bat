@echo off
REM Builds ONLY Macondo WorkLogger (time logging). Double-click this file.
REM Result: dist\MacondoWorkLogger.exe
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")

%PY% --version >nul 2>nul
if errorlevel 1 (
    echo Python not found. Install Python 3.11+ from python.org and check "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
%PY% -m pip install --upgrade -r requirements.txt pyinstaller || goto :error

echo [2/3] Cleaning up the previous build...
if exist build rmdir /s /q build

echo [3/3] Building MacondoWorkLogger.exe (takes a few minutes)...
%PY% -m PyInstaller MacondoWorkLogger.spec --noconfirm || goto :error

echo.
echo Done: dist\MacondoWorkLogger.exe
pause
exit /b 0

:error
echo.
echo The build failed. Copy the text above to review it.
pause
exit /b 1
