@echo off
cd /d "%~dp0"

if exist "PubMed Reference Converter.exe" (
    start "" "PubMed Reference Converter.exe"
    exit /b
)

where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw gui.py
    exit /b
)

echo.
echo PubMed GUI could not start.
echo.
echo Build installer:  build_installer.bat
echo.
pause
