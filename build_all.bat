@echo off
REM Builds all THREE executables at once. Double-click this file.
REM Result: dist\MacondoLogger.exe, dist\MacondoWorkLogger.exe, dist\MacondoSuite.exe
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")

%PY% --version >nul 2>nul
if errorlevel 1 (
    echo Python not found. Install Python 3.11+ from python.org and check "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [1/5] Installing dependencies...
%PY% -m pip install --upgrade -r requirements.txt pyinstaller || goto :error

echo [2/5] Cleaning up previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/5] Building MacondoLogger.exe...
%PY% -m PyInstaller MacondoLogger.spec --noconfirm || goto :error
if exist build rmdir /s /q build

echo [4/5] Building MacondoWorkLogger.exe...
%PY% -m PyInstaller MacondoWorkLogger.spec --noconfirm || goto :error
if exist build rmdir /s /q build

echo [5/5] Building MacondoSuite.exe...
%PY% -m PyInstaller MacondoSuite.spec --noconfirm || goto :error

echo.
echo Done. In the dist\ folder you have:
echo   - MacondoLogger.exe       (Bug Logger only)
echo   - MacondoWorkLogger.exe   (time logging only)
echo   - MacondoSuite.exe        (both, in tabs)
pause
exit /b 0

:error
echo.
echo The build failed. Copy the text above to review it.
pause
exit /b 1
