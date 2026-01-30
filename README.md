# GifCap

A simple, open-source screen recorder for Linux built with Rust. Captures selected areas and saves them as high-quality animated GIFs.

## Usage

1.  **Launch**: Open GifCap.
2.  **Position**: Drag the window over the area you want to record. The transparent window acts as your viewfinder.
3.  **Record**: Click **Rec** to start capturing.
4.  **Stop**: Click **Stop** when finished.
5.  **Edit**: (Optional) Remove unwanted frames or adjust the delay.
6.  **Save**: Export your recording as a GIF.

## Features

*   **Smart Capture**: Records strictly the area under the window, ignoring the app UI itself.
*   **Editor**: Built-in frame editor to trim recordings.
*   **Performance**: High-performance capturing (up to 60fps) using X11 shared memory.
*   **Theming**: Adwaita Dark theme integration.
*   **Portable**: Available as AppImage, Flatpak, Deb, and RPM.)
