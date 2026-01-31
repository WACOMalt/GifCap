#!/bin/bash
set -e

VERSION="1.1.0"
DIST_DIR="$(pwd)/dist"
mkdir -p "$DIST_DIR"

echo "Building GifCap v$VERSION..."

# 1. Build Binary
cargo build --release

# 2. Standalone Zip
echo "Creating Zip..."
rm -rf GifCap_Standalone
mkdir -p GifCap_Standalone
cp target/release/gifcap GifCap_Standalone/
cp -r resources GifCap_Standalone/
cp README.md GifCap_Standalone/
zip -r "$DIST_DIR/GifCap_${VERSION}_Linux_x64_Standalone.zip" GifCap_Standalone
rm -rf GifCap_Standalone

# 3. AppImage
echo "Creating AppImage..."
# Assumes AppDir already exists and linuxdeploy is present (as per current env)
cp target/release/gifcap AppDir/usr/bin/gifcap
./linuxdeploy --appdir AppDir --output appimage --desktop-file resources/bsums.xyz.gifcap.desktop --icon-file resources/icons/bsums.xyz.gifcap.png
mv GifCap-*.AppImage "$DIST_DIR/GifCap_${VERSION}_Linux_x64.AppImage"

# 4. Debian Package
echo "Creating DEB..."
mkdir -p deb_package/usr/bin
cp target/release/gifcap deb_package/usr/bin/
dpkg-deb --build deb_package "$DIST_DIR/GifCap_${VERSION}_Linux_x64.deb"

# 5. RPM Package
echo "Creating RPM..."
rm -rf rpmbuild/RPMS
mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cp target/release/gifcap rpmbuild/BUILD/gifcap
rpmbuild --define "_topdir $(pwd)/rpmbuild" -bb rpmbuild/SPECS/gifcap.spec
cp rpmbuild/RPMS/x86_64/*.rpm "$DIST_DIR/GifCap_${VERSION}_Linux_x64.rpm"

# 6. Flatpak
echo "Creating Flatpak..."
# Assumes build-dir and repo are managed or clean
flatpak-builder --user --install --force-clean build-dir bsums.xyz.gifcap.yml
flatpak build-bundle ~/.local/share/flatpak/repo "$DIST_DIR/GifCap_${VERSION}_Linux_x64.flatpak" bsums.xyz.gifcap

echo "Done! Artifacts in $DIST_DIR"
ls -lh "$DIST_DIR"
