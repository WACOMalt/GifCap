# GifCam Reverse Engineering Findings

This document contains research and analysis of the original GifCam Windows application by BahraniApps.

## Application Overview

**GifCam** is a Windows desktop application for creating animated GIFs by recording a portion of the screen. It features a unique "cutout window" design where the center of the application is transparent, showing the desktop behind it. Anything visible through this cutout is recorded when the user starts capture.

## UI Structure

### Main Recording Window

The recording window consists of:
- **Transparent Cutout Region**: Center-left portion of the window that shows the desktop underneath
- **Control Panel**: Right-hand sidebar containing:
  - `Rec` button - Start recording
  - `Frame` button - Capture single frame
  - `Edit` button - Open frame editor
  - `Save` button - Export to GIF
  - FPS selector (dropdown with 3 preset values)
  - Frame counter display

### Frame Editor Window

A separate window that displays captured frames:
- **Frame Strip**: Horizontal layout showing all frames left-to-right
- **Scrolling**: Mouse wheel navigation through frames
- **Right-click Context Menu**:
  - Delete frame
  - Delete from frame to beginning
  - Delete from frame to end
  - Delete even-numbered frames
  - Add text overlay
  - Resize frames
  - "Yoyo" effect (reverse playback)
  - **Keyboard Entry**: Dialog to set frame delay (ms) for current or all frames

### Customization Menu

Settings dialog (accessed via keyboard shortcut):
- **FPS Presets**: Configure 3 custom frame rates (default: 10, 16, 33 FPS)
- **Memory Limit**: Default 1GB cap for RAM storage
- **Storage Mode**: Toggle between RAM and disk storage
- **Cursor Capture**: Option to always capture cursor

## Core Features

### Smart Recording Algorithm

GifCam uses an intelligent approach to minimize file size:

1. **Frame Comparison**: Each new frame is compared to the previous one
2. **Identical Frame Handling**: If frames are identical, no new image is saved - instead, the delay is increased
3. **Pixel Differencing**: Only changed pixels are saved (using a "green screen" transparent color for unchanged regions)
4. **Optimization Result**: Significant file size reduction compared to naïve frame-by-frame capture

### Storage Modes

- **RAM Storage (Default)**:
  - Frames stored uncompressed in memory
  - Fast but limited (~200 frames typical before hitting memory cap)
  - Default 1GB limit
  
- **Disk Storage** (v4.0+):
  - Frames stored in `%UserProfile%\AppData\Local\Temp\GifCamTemporaryFrames`
  - Allows longer recordings
  - Activated via "Shift + New" shortcut or settings toggle

### Export Options

When saving, GifCam offers multiple color reduction modes:
- **Quantize**: Intelligent color palette selection
- **256 Colors**: Standard GIF palette
- **20 Colors**: Aggressive reduction
- **Grayscale**: Black and white
- **Monochrome**: 2-color output

- **Preview**: Shows resulting GIF and estimated file size before saving

## Technical Implementation

### Platform & Language
- **Platform**: Windows only
- **Language**: Delphi (Object Pascal)
- **APIs**: Uses Windows-specific APIs for:
  - Window transparency (layered windows)
  - Screen capture (BitBlt/DirectX)
  - Shape regions (SetWindowRgn)

### Limitations Observed

1. **~200 Frame Limit**: When using RAM storage, memory constraints limit recording length
2. **3 FPS Presets Only**: Changing frame rates requires going to customization menu
3. **Windows-Only**: No native Linux or macOS support

## Version History Highlights

### Version 2.0 (2013)
- Added "Same as the previous frame" delay accumulation
- Introduced green screen optimization

### Version 3.0 (2014)
- Added Edit mode with frame manipulation
- Keyboard shortcuts added

### Version 4.0 (2016)
- **Disk storage mode** added (major feature for longer recordings)
- "Shift + New" shortcut

### Version 5.0 (2017)
- Frame resizing in editor
- Anti-aliasing support

### Version 6.0 (2019)
- "Yoyo" effect
- Improved color quantization

### Version 7.0+ (2021-2023)
- Multi-monitor support improvements
- Additional keyboard shortcuts
- UI refinements

## Research Assets

Browser recording of original GifCam website exploration:

![Browser Recording](file:///home/wacomalt/Documents/GifCap/reverse-engineering/gifcam_research_1769275194194.webp)

Screenshots showing features and UI:

````carousel
![Main page overview](file:///home/wacomalt/Documents/GifCap/reverse-engineering/screenshots/gifcam_main_page_1769275237975.png)
<!-- slide -->
![Features and recording details](file:///home/wacomalt/Documents/GifCap/reverse-engineering/screenshots/gifcam_features_middle_1769275246961.png)
<!-- slide -->
![Saving options and color modes](file:///home/wacomalt/Documents/GifCap/reverse-engineering/screenshots/gifcam_saving_options_1769275258065.png)
<!-- slide -->
![Version history - early versions](file:///home/wacomalt/Documents/GifCap/reverse-engineering/screenshots/gifcam_versions_1_1769275269613.png)
<!-- slide -->
![Version history - mid versions](file:///home/wacomalt/Documents/GifCap/reverse-engineering/screenshots/gifcam_versions_2_1769275287206.png)
````

## Key Insights for GifCap Implementation

### Must-Have Features to Port
1. ✅ Transparent cutout window design
2. ✅ Smart frame comparison algorithm
3. ✅ Disk-based storage for unlimited recording
4. ✅ Frame editor with full deletion operations
5. ✅ Keyboard entry for frame delays
6. ✅ GIF export with color reduction

### Improvements for GifCap
1. 🎯 **Simple FPS Input**: Replace 3-preset system with direct integer input field
2. 🎯 **Default to Disk Storage**: Start with unlimited capacity mode enabled
3. 🎯 **Settings Persistence**: Remember FPS and window settings automatically
4. 🎯 **Cross-Platform**: Design for Linux first, then Windows/Mac branches

### Technical Challenges
1. **Transparent Regions on Linux**: Need X11 shape extension or Wayland-compatible approach
2. **Screen Capture**: Use cross-platform library (mss, python-xlib, or similar)
3. **GIF Encoding**: Leverage imageio/PIL instead of custom encoder
4. **Frame Comparison**: Implement pixel-diff algorithm similar to GifCam's green screen method

## References

- Official Website: https://blog.bahraniapps.com/gifcam/
- Latest Version: 7.7 (as of research date)
- License: Freeware (proprietary)
