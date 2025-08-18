@echo off
echo Building CaseCon installer...
echo.

echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Creating executable...
pyinstaller CaseCon.spec --clean

if not exist "dist\CaseCon.exe" (
    echo ERROR: Failed to create executable!
    pause
    exit /b 1
)

echo.
echo Step 3: Creating installer...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_exe.iss
    echo.
    echo SUCCESS! Your installer is ready in the installer_output folder!
) else (
    echo Inno Setup not found. Please:
    echo 1. Install Inno Setup from https://jrsoftware.org/isinfo.php
    echo 2. Open setup_exe.iss in Inno Setup
    echo 3. Click Compile
)

echo.
pause