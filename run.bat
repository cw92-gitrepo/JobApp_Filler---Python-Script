@echo off
rem Double-click to run Job App Script.
rem   1. Setup, at most once a week: the first run finds Python (3.10 or newer),
rem      creates a private .venv folder and installs the requirements; later
rem      weekly checks only update the requirements.
rem   2. Opens Chrome with remote debugging if it isn't already open that way.
rem   3. Starts the app. This window shows progress messages; leave it open.
setlocal
cd /d "%~dp0"
title Job App Script

rem --- 1. Setup (at most once a week) -----------------------------------------
rem .venv\last_setup.txt is rewritten after each successful setup, so its date
rem says when setup last ran. "forfiles /d -7" only matches it once it's 7 or
rem more days old; no match (errorlevel 1) means setup is still fresh.
set "VENV_PY=.venv\Scripts\python.exe"
set "STAMP=.venv\last_setup.txt"
if not exist "%VENV_PY%" goto :first_setup
if not exist "%STAMP%" goto :weekly_setup
forfiles /p .venv /m last_setup.txt /d -7 >nul 2>&1
if errorlevel 1 goto :setup_done
goto :weekly_setup

:first_setup
rem "--version" is used instead of "where": the Microsoft Store "python" alias
rem exists even when Python isn't installed, but it fails when run.
set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto :have_python
python --version >nul 2>&1
if not errorlevel 1 set "PY=python"
if not defined PY goto :no_python
:have_python
echo First run: installing what the app needs. This takes a minute...
%PY% -m venv .venv
if errorlevel 1 goto :setup_failed
"%VENV_PY%" -c "import sys; sys.exit(sys.version_info < (3, 10))"
if errorlevel 1 goto :old_python
"%VENV_PY%" -m pip install --quiet --upgrade pip
"%VENV_PY%" -m pip install --quiet -r requirements.txt
if errorlevel 1 goto :setup_failed
echo %date% > "%STAMP%"
echo Done.
goto :setup_done

:weekly_setup
rem The app already works, so a failed update (e.g. offline) only warns.
echo Weekly check: updating the app's packages...
"%VENV_PY%" -m pip install --quiet --upgrade -r requirements.txt
if errorlevel 1 (
    echo Couldn't update the packages; starting with the ones already installed.
) else (
    echo %date% > "%STAMP%"
)
:setup_done

rem --- 2. Chrome with remote debugging -----------------------------------------
rem A separate --user-data-dir starts a separate Chrome, so your normal Chrome
rem can stay open. It has its own logins: sign into the job portal there once.
curl --silent --output nul --max-time 2 http://localhost:9222/json/version
if not errorlevel 1 goto :chrome_ready
set "CHROME="
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set "CHROME=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set "CHROME=%LocalAppData%\Google\Chrome\Application\chrome.exe"
if not defined CHROME goto :no_chrome
start "" "%CHROME%" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\chrome-profile"
echo Opened Chrome. Sign into the job portal in that window (first time only),
echo open an application, then click "Launch script".
:chrome_ready

rem --- 3. Run --------------------------------------------------------------------
"%VENV_PY%" main.py
if errorlevel 1 goto :crashed
exit /b 0

rem --- Problems -------------------------------------------------------------------
:no_python
echo Python isn't installed. Install Python 3.10 or newer from https://www.python.org/downloads/
echo (tick "Add python.exe to PATH" in the installer), then double-click run.bat again.
goto :wait

:old_python
echo This app needs Python 3.10 or newer. Install it from https://www.python.org/downloads/,
echo delete the .venv folder next to run.bat, then double-click run.bat again.
goto :wait

:setup_failed
echo Installing the app's packages failed (see the messages above).
echo Check your internet connection, delete the .venv folder, and try again.
goto :wait

:no_chrome
echo Couldn't find Google Chrome. Install it from https://www.google.com/chrome/ and try again.
goto :wait

:crashed
echo The app stopped with an error (see the messages above).

:wait
pause
exit /b 1
