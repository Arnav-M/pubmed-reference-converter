@echo off
setlocal
cd /d "%~dp0"

echo.
echo === PubMed Reference Converter installer build ===
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Installing build tools...
python -m pip install -q -r requirements-gui.txt pyinstaller
if errorlevel 1 goto fail

echo [2/3] Building PubMed Reference Converter.exe...
python -m PyInstaller pubmed-gui.spec --noconfirm --clean
if errorlevel 1 goto fail
if not exist "dist\PubMed Reference Converter.exe" (
    echo Build failed: dist\PubMed Reference Converter.exe not found.
    goto fail
)

set "ISCC="
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if exist "%LocalAppData%\Programs\Inno Setup 7\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 7\ISCC.exe"
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if "%ISCC%"=="" (
    echo.
    echo [3/3] Inno Setup not installed.
    echo.
    echo Download the free compiler once:
    echo   https://jrsoftware.org/isdl.php
    echo.
    echo Portable app is ready at: dist\PubMed Reference Converter.exe
    echo Re-run this file after installing Inno Setup to create the setup wizard.
    echo.
    pause
    exit /b 0
)

echo [3/3] Creating Windows installer...
"%ISCC%" installer\PubMedConverter.iss
if errorlevel 1 goto fail

echo.
echo Done!
echo   Installer: installer\output\PubMed-Reference-Converter-Setup.exe
echo   Portable:  dist\PubMed Reference Converter.exe
echo.
echo Upload the Setup.exe to GitHub Releases for end users.
echo.
pause
exit /b 0

:fail
echo.
echo Build failed.
pause
exit /b 1
