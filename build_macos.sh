#!/bin/bash
set -e

VERSION="1.1.1"
APP_NAME="GifCap"
BUNDLE_NAME="${APP_NAME}.app"
DIST_DIR="$(pwd)/dist"

echo "Building $APP_NAME v$VERSION for macOS..."

# 1. Clean and Build
rm -rf "$BUNDLE_NAME"
cargo build --release

# 2. Create Bundle Structure
mkdir -p "$BUNDLE_NAME/Contents/MacOS"
mkdir -p "$BUNDLE_NAME/Contents/Resources"

# 3. Copy Binaries and Config
cp target/release/gifcap "$BUNDLE_NAME/Contents/MacOS/"
cp macos/Info.plist "$BUNDLE_NAME/Contents/"

# 4. Copy Resources (Fonts, Icons)
# Note: In a real mac app, icons should be .icns. For now, we copy the png ensuring it's available.
# We also need to make sure the binary can find the fonts if they are loaded from relative paths.
# GifCap embeds fonts in src/main.rs using include_bytes!, so no file copy needed for fonts.

# Icons: simplest is to just drop it inResources.
# A proper .icns is better, but passing a png often works or we can convert it if we had tools.
cp resources/icons/bsums.xyz.gifcap.png "$BUNDLE_NAME/Contents/Resources/AppIcon.png"

echo "Created $BUNDLE_NAME"

# 5. Package into Zip
mkdir -p "$DIST_DIR"
zip -r "$DIST_DIR/${APP_NAME}_${VERSION}_MacOS_x64.zip" "$BUNDLE_NAME"

echo "Artifacts in $DIST_DIR"
