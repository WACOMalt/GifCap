# GifCap

A simple, open-source screen recorder for Linux built with Rust. Captures selected areas and saves them as high-quality animated GIFs.

## IMPORTANT VIBE-CODING/AI/LLM NOTE
This app is vibe-coded with Claude Opus and Gemini. As such, I offer no assurances to code quality, safety, etc. By using this app, you accept that it may suck. The code is here if you want to look through it.
I plan to continue directing the maintenance of this app, but no promises.  Feel free to fork it to make it better or just as reference. I have asked the coding agents to ensure only FOSS code was use

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
