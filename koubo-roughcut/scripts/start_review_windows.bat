@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"
set "PYTHON=%REPO_ROOT%\koubo-roughcut\.venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo Python environment not found: "%PYTHON%"
  echo Create the environment and install requirements first. See README.md.
  pause
  exit /b 1
)

"%PYTHON%" "%SCRIPT_DIR%launch_review.py"
if errorlevel 1 pause
