# Building GifCap for Linux

Complete guide for building and distributing GifCap packages.

---

## Quick Start

### Build All Packages
```bash
./build-linux.sh all
```

### Build Specific Package
```bash
./build-linux.sh flatpak    # Flatpak only
./build-linux.sh appimage   # AppImage only
./build-linux.sh deb        # DEB only
./build-linux.sh rpm        # RPM only
```

All built packages will be in `./dist/`

---

## Prerequisites

### For All Builds
- Python 3.10+
- Git

### For Flatpak
```bash
sudo apt install flatpak flatpak-builder
```

### For AppImage
```bash
sudo apt install python3-venv
```

### For DEB
```bash
sudo apt install dpkg-dev debhelper dh-python
```

### For RPM
```bash
sudo dnf install rpm-build
```

---

## Package Details

### Flatpak (Recommended)
- **Output:** `dist/GifCap.flatpak`
- **Install:** `flatpak install GifCap.flatpak`
- **Run:** `flatpak run com.gifcap.GifCap`
- **Features:**
  - Sandboxed and secure
  - Bundles all dependencies including `grim`
  - Cross-distribution compatibility

### AppImage
- **Output:** `dist/GifCap-x86_64.AppImage`
- **Run:** `./GifCap-x86_64.AppImage`
- **Features:**
  - Single portable executable
  - No installation required
  - Works on any Linux distribution

### DEB Package
- **Output:** `dist/gifcap_1.0.0-1_all.deb`
- **Install:** `sudo apt install ./gifcap_1.0.0-1_all.deb`
- **Run:** `gifcap`
- **Platforms:** Debian, Ubuntu, Linux Mint, Pop!_OS

### RPM Package
- **Output:** `dist/gifcap-1.0.0-1.noarch.rpm`
- **Install:** `sudo rpm -ivh gifcap-1.0.0-1.noarch.rpm`
- **Run:** `gifcap`
- **Platforms:** Fedora, RHEL, CentOS, openSUSE

---

## Testing

### Test AppImage Locally
```bash
cd appimage
./build.sh
./GifCap-x86_64.AppImage
```

### Test Flatpak Locally
```bash
flatpak-builder --user --install --force-clean build-dir flatpak/com.gifcap.GifCap.yml
flatpak run com.gifcap.GifCap
```

### Test DEB Package
```bash
./build-linux.sh deb
sudo apt install ./dist/gifcap_*.deb
gifcap
```

### Test RPM Package
```bash
./build-linux.sh rpm
sudo rpm -ivh dist/gifcap-*.rpm
gifcap
```

---

## Distribution

### Flathub (Recommended)
1. Fork this repository
2. Submit PR to https://github.com/flathub/flathub
3. Follow Flathub review process
4. Automatic builds and updates

### GitHub Releases
```bash
# Build all packages
./build-linux.sh all

# Create release
gh release create v1.0.0 \
  dist/GifCap.flatpak \
  dist/GifCap-x86_64.AppImage \
  dist/gifcap_*.deb \
  dist/gifcap-*.rpm \
  --title "GifCap v1.0.0" \
  --notes "Initial release"
```

### Package Repositories

**Debian/Ubuntu PPA:**
```bash
dput ppa:yourname/gifcap gifcap_1.0.0-1_source.changes
```

**Fedora COPR:**
```bash
copr-cli build yourname/gifcap dist/gifcap-1.0.0-1.src.rpm
```

---

## Troubleshooting

### Flatpak build fails
- Ensure flatpak-builder is installed
- Check manifest syntax with `flatpak-builder --check flatpak/com.gifcap.GifCap.yml`

### AppImage doesn't run
- Check if Python dependencies are properly bundled
- Verify file has execute permissions: `chmod +x GifCap-x86_64.AppImage`

### DEB dependency errors
- Install missing dependencies: `sudo apt-get install -f`
- Verify dependencies in `debian/control`

### RPM build fails
- Ensure rpmbuild directories exist: `mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}`
- Check spec file syntax

---

## File Structure

```
GifCap/
├── build-linux.sh          # Master build script
├── flatpak/
│   └── com.gifcap.GifCap.yml
├── appimage/
│   ├── build.sh
│   └── gifcap.spec
├── debian/
│   ├── control
│   ├── rules
│   └── changelog
├── rpm/
│   └── gifcap.spec
├── resources/
│   ├── com.gifcap.GifCap.desktop
│   └── icons/
│       └── com.gifcap.GifCap.png
└── dist/                   # Build outputs
```

---

## Dependencies

**Python Packages** (from requirements.txt):
- PyQt6 >= 6.4.0
- Pillow >= 9.0.0
- imageio[ffmpeg] >= 2.25.0
- mss >= 7.0.0

**Optional System Packages:**
- `grim` - For Wayland screen capture (bundled in Flatpak, recommended for others)

---

## Notes

- **No xdotool required:** Cursor tracking uses Qt (no external dependencies)
- **Wayland support:** Requires `grim` (automatically bundled in Flatpak)
- **X11 support:** Works out of the box with `mss` library
