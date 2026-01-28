# GifCap v1.0.0 - Initial Release

Screen recorder for creating animated GIFs with transparent capture window, frame editing, and optimized encoding.

## Features

✨ **Transparent Recording Window**
- Click-through support - interact with windows beneath
- Drag and resize to frame exactly what you want

🎬 **Smart Recording**
- Hybrid X11/Wayland support
- Intelligent frame comparison reduces file size
- Cursor capture with compositing
- Adjustable FPS (1-60)

✏️ **Built-in Frame Editor**
- Delete unwanted frames
- Adjust per-frame delays
- Preview before export

📦 **Cross-Platform Packaging**
- DEB package for Debian/Ubuntu
- Build configurations for Flatpak, AppImage, RPM

## Downloads

### Debian/Ubuntu
**gifcap_1.0.0-1_all.deb** (361 KB)

```bash
sudo apt install ./gifcap_1.0.0-1_all.deb
gifcap
```

### Fedora/RHEL
**gifcap-1.0.0-1.noarch.rpm** (372 KB)

```bash
sudo rpm -ivh gifcap-1.0.0-1.noarch.rpm
gifcap
```

### AppImage (Portable)
**GifCap-x86_64.AppImage** (~108 MB)

```bash
chmod +x GifCap-x86_64.AppImage
./GifCap-x86_64.AppImage
```

### Flatpak
**bsums.xyz.gifcap.flatpak** (Coming soon)

```bash
flatpak install bsums.xyz.gifcap.flatpak
flatpak run bsums.xyz.gifcap
```

### Other Formats

Build instructions available in [BUILDING.md](https://github.com/WACOMalt/GifCap/blob/main/BUILDING.md):

- **Flatpak**: `./build-linux.sh flatpak`
- **AppImage**: `./build-linux.sh appimage`  
- **RPM**: `./build-linux.sh rpm`

## Requirements

- Python 3.10+
- PyQt6
- PIL (Pillow)
- imageio
- mss

DEB package installs dependencies automatically.

## Usage

1. Launch GifCap
2. Position and resize the transparent window
3. Click **Rec** to start recording
4. Click **Stop** when done
5. Edit frames if needed
6. Click **Save** to export GIF

## Known Issues

- Wayland capture requires `grim` to be installed separately
- Some window managers may not support transparency

## What's Next

- Submit to Flathub for wider distribution
- macOS and Windows ports
- Additional export formats (MP4, WebP)

---

**MIT License** | [GitHub](https://github.com/WACOMalt/GifCap) | [Report Issues](https://github.com/WACOMalt/GifCap/issues)
