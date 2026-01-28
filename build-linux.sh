#!/bin/bash
# Master build script for all Linux packages of GifCap

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   GifCap Linux Package Build Script   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo

# Parse arguments
BUILD_FLATPAK=false
BUILD_APPIMAGE=false
BUILD_DEB=false
BUILD_RPM=false
BUILD_ALL=false

if [ $# -eq 0 ] || [ "$1" == "all" ]; then
    BUILD_ALL=true
else
    for arg in "$@"; do
        case $arg in
            flatpak) BUILD_FLATPAK=true ;;
            appimage) BUILD_APPIMAGE=true ;;
            deb) BUILD_DEB=true ;;
            rpm) BUILD_RPM=true ;;
            *)
                echo -e "${RED}Unknown option: $arg${NC}"
                echo "Usage: $0 [all|flatpak|appimage|deb|rpm]"
                exit 1
                ;;
        esac
    done
fi

# Set flags if building all
if [ "$BUILD_ALL" = true ]; then
    BUILD_FLATPAK=true
    BUILD_APPIMAGE=true
    BUILD_DEB=true
    BUILD_RPM=true
fi

# Version configuration
VERSION="1.0.0"
ARCH="x86_64"

# Create output directory
mkdir -p dist

# Build Flatpak
if [ "$BUILD_FLATPAK" = true ]; then
    echo -e "${YELLOW}Building Flatpak...${NC}"
    if command -v flatpak-builder &> /dev/null; then
        cd flatpak
        flatpak-builder --force-clean --repo=repo --disable-cache build-dir bsums.xyz.gifcap.yml
        flatpak build-bundle repo "../dist/GifCap-${VERSION}-${ARCH}.flatpak" bsums.xyz.gifcap
        cd ..
        echo -e "${GREEN}✓ Flatpak built: dist/GifCap-${VERSION}-${ARCH}.flatpak${NC}"
    else
        echo -e "${RED}✗ flatpak-builder not found. Install with: sudo apt install flatpak-builder${NC}"
    fi
    echo
fi

# Build AppImage
if [ "$BUILD_APPIMAGE" = true ]; then
    echo -e "${YELLOW}Building AppImage...${NC}"
    cd appimage
    if ./build.sh; then
        # AppImage builder already generates versioned name, but let's enforce our naming
        find . -name "GifCap-*.AppImage" -exec mv {} "../dist/GifCap-${VERSION}-${ARCH}.AppImage" \;
        echo -e "${GREEN}✓ AppImage built: dist/GifCap-${VERSION}-${ARCH}.AppImage${NC}"
    else
        echo -e "${RED}✗ AppImage build failed${NC}"
    fi
    cd ..
    echo
fi

# Build DEB
if [ "$BUILD_DEB" = true ]; then
    echo -e "${YELLOW}Building DEB package...${NC}"
    if command -v dpkg-buildpackage &> /dev/null; then
        dpkg-buildpackage -us -uc -b
        mv ../gifcap_*.deb "dist/GifCap-${VERSION}-${ARCH}.deb" 2>/dev/null || true
        echo -e "${GREEN}✓ DEB package built: dist/GifCap-${VERSION}-${ARCH}.deb${NC}"
    else
        echo -e "${RED}✗ dpkg-buildpackage not found. Install with: sudo apt install dpkg-dev${NC}"
    fi
    echo
fi

# Build RPM
if [ "$BUILD_RPM" = true ]; then
    echo -e "${YELLOW}Building RPM package...${NC}"
    if command -v rpmbuild &> /dev/null; then
        # Create tarball
        tar czf "gifcap-${VERSION}.tar.gz" --transform "s,^,gifcap-${VERSION}/," src resources README.md LICENSE
        
        # Move to rpmbuild directory
        mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
        cp "gifcap-${VERSION}.tar.gz" ~/rpmbuild/SOURCES/
        cp rpm/gifcap.spec ~/rpmbuild/SPECS/
        
        # Build
        rpmbuild -ba ~/rpmbuild/SPECS/gifcap.spec
        
        # Copy result
        cp ~/rpmbuild/RPMS/noarch/gifcap-*.rpm "dist/GifCap-${VERSION}-${ARCH}.rpm"
        
        # Cleanup
        rm "gifcap-${VERSION}.tar.gz"
        
        echo -e "${GREEN}✓ RPM package built: dist/GifCap-${VERSION}-${ARCH}.rpm${NC}"
    else
        echo -e "${RED}✗ rpmbuild not found. Install with: sudo dnf install rpm-build${NC}"
    fi
    echo
fi

# Summary
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Build Complete!              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo
echo "Built packages are in: ./dist/"
ls -lh dist/ 2>/dev/null || echo "No packages built"
