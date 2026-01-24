# GifCap

A Linux-first, simple, GIF format screen-capturing tool. Inspired by the amazing tool "GifCam" by BahraniApps, but built from the ground up to be Cross-platform.

## Features

- **Transparent Cutout Window**: Record exactly what you see through the app's transparent center region
- **Unlimited Recording**: Disk-based frame storage eliminates the ~200 frame limit
- **Simple FPS Control**: Direct input field for framerate, instead of clunky presets you have to configure ahead of time.
- **Smart Compression**: Only saves changed pixels between frames for smaller file sizes
- **Frame Editor**: Full control over captured frames with deletion and timing adjustments
- **Settings Persistence**: Automatically remembers your FPS and window preferences
- **Multiple output optimization options**: Implementing ImageMagick, FFMpeg, and Gifsicle for exports.

## Requirements

- Linux with X11 (or XWayland)
- Python 3.8+
- PyQt6
- Screen capture capability

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GifCap.git
cd GifCap
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

### Controls

- **Rec**: Start/stop recording
- **Frame**: Capture a single frame
- **Edit**: Open frame editor (after capturing frames)
- **Save**: Export to GIF
- **FPS Field**: Set recording frame rate (remembers last setting)

### Frame Editor

Right-click on any frame to:
- Delete frame
- Delete from frame to beginning
- Delete from frame to end
- Delete even-numbered frames
- Set frame delay (current or all frames)

## Platform Support

- **Linux**: Primary supported platform
- **Windows**: Planned (separate branch)
- **macOS**: Planned (separate branch)

## Credits

Inspired by [GifCam](https://blog.bahraniapps.com/gifcam/) by BahraniApps.

## License

MIT License - See LICENSE file for details
