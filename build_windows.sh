#!/bin/bash
set -e

VERSION="1.1.1"
DIST_DIR="$(pwd)/dist"
mkdir -p "$DIST_DIR"

echo "Building GifCap v$VERSION for Windows..."

# 1. Build Binary (Cross-compile)
cargo build --release --target x86_64-pc-windows-gnu

# 2. Standalone Zip
echo "Creating Windows Zip..."
rm -rf GifCap_Windows
mkdir -p GifCap_Windows
cp target/x86_64-pc-windows-gnu/release/gifcap.exe GifCap_Windows/

cp README.md GifCap_Windows/
cd GifCap_Windows
rm -f "$DIST_DIR/GifCap_${VERSION}_Windows_x64_Standalone.zip"
zip -r "$DIST_DIR/GifCap_${VERSION}_Windows_x64_Standalone.zip" .
cd ..
rm -rf GifCap_Windows

# 3. Installer (NSIS)
echo "Creating Installer..."
# Create a temporary directory for NSIS to pack
mkdir -p nsis_build
cp target/x86_64-pc-windows-gnu/release/gifcap.exe nsis_build/
cp -r resources nsis_build/
cp README.md nsis_build/

makensis installer.nsi
mv GifCap_Installer.exe "$DIST_DIR/GifCap_${VERSION}_Windows_x64_Installer.exe"
rm -rf nsis_build

echo "Done! Artifacts in $DIST_DIR"
ls -lh "$DIST_DIR"
