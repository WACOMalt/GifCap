#!/bin/bash
# AppImage build script for GifCap

set -e

echo "Building GifCap AppImage..."

# Clean previous builds
rm -rf build dist AppDir *.AppImage

# Create virtual environment for building
python3 -m venv build_env
source build_env/bin/activate

# Install dependencies
pip install -r ../requirements.txt
pip install pyinstaller

# Build with PyInstaller
echo "Running PyInstaller..."
pyinstaller gifcap.spec

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppDir structure
echo "Creating AppDir..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/512x512/apps

# Copy files
cp dist/gifcap AppDir/usr/bin/
cp ../resources/com.gifcap.GifCap.desktop AppDir/gifcap.desktop
cp ../resources/com.gifcap.GifCap.desktop AppDir/usr/share/applications/
cp ../resources/icons/com.gifcap.GifCap.png AppDir/gifcap.png
cp ../resources/icons/com.gifcap.GifCap.png AppDir/usr/share/icons/hicolor/512x512/apps/

# Create AppRun script
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/gifcap" "$@"
EOF
chmod +x AppDir/AppRun

# Build AppImage
echo "Building AppImage..."
ARCH=x86_64 ./appimagetool-x86_64.AppImage AppDir GifCap-x86_64.AppImage

echo "✅ AppImage created: GifCap-x86_64.AppImage"
ls -lh GifCap-x86_64.AppImage
