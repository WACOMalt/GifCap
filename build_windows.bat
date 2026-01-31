@echo off
set VERSION=1.1.0
set DIST_DIR=dist

mkdir %DIST_DIR%

echo Building GifCap v%VERSION% for Windows...

:: 1. Build Binary
cargo build --release

:: 2. Standalone Zip
echo Creating Windows Zip...
if exist GifCap_Windows rmdir /s /q GifCap_Windows
mkdir GifCap_Windows
copy target\release\gifcap.exe GifCap_Windows\

copy README.md GifCap_Windows\
cd GifCap_Windows
if exist ..\%DIST_DIR%\GifCap_%VERSION%_Windows_x64_Standalone.zip del ..\%DIST_DIR%\GifCap_%VERSION%_Windows_x64_Standalone.zip
powershell Compress-Archive -Path * -DestinationPath ..\%DIST_DIR%\GifCap_%VERSION%_Windows_x64_Standalone.zip -Force
cd ..
rmdir /s /q GifCap_Windows

:: 3. Installer (NSIS)
echo Creating Installer...
if exist nsis_build rmdir /s /q nsis_build
mkdir nsis_build
copy target\release\gifcap.exe nsis_build\
xcopy resources nsis_build\resources /E /I
copy README.md nsis_build\

makensis installer.nsi
move GifCap_Installer.exe %DIST_DIR%\GifCap_%VERSION%_Windows_x64_Installer.exe
rmdir /s /q nsis_build

echo Done! Artifacts in %DIST_DIR%
