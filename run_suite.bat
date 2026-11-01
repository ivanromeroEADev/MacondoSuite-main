@echo off
REM Runs Macondo Suite (Bug Logger + WorkLogger in tabs) WITHOUT building it. Double-click.
REM It opens in the browser. To close it, close this black window.
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")

%PY% --version >nul 2>nul
if errorlevel 1 (
    echo Python not found. Install Python 3.11+ from python.org and check "Add python.exe to PATH".
    pause
    exit /b 1
)

echo Installing dependencies (only slow the first time)...
%PY% -m pip install -r requirements.txt

echo Opening Macondo Suite in the browser...
%PY% -m streamlit run macondo_suite_app.py
pause
