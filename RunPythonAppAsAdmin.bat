@echo off
:: Checking if the script is running with administrator privileges
NET SESSION >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Running with administrator privileges...
    :: Running the same script with administrator privileges
    powershell -Command "Start-Process cmd -ArgumentList '/c %~dp0%~nx0' -Verb RunAs"
    exit /b
)

:: Running the Python file located in the same directory as the script
python "%~dp0BlockedSitesManager_Eng.py"
