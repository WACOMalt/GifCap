# GifCap

A simple, open-source screen recorder for Linux, Windows, and macOS, built with Rust. 
Captures selected areas and saves them as high-quality animated GIFs.

## IMPORTANT VIBE-CODING / AI / LLM NOTE
This app is vibe-coded, using Google Antigravity IDE, and Claude Opus and Gemini. I offer no assurances to code quality, safety, etc. By using this app, you accept that it may suck. The code is here if you want to look through it.

I plan to continue directing the maintenance of this app, but no promises.  Feel free to fork it to make it better or just as reference. Treat this entire github repo as an unstable artifact.

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
*   **Portable**: Available as installed packages, and as standalone binaries.

## Release Structure
*   **GifCap_X.X.x_Linux_x64.AppImage**
    Linux AppImage - VERIFIED FUNCTIONAL
    
*   **GifCap_X.X.X_Linux_x64.deb**
    Debian installer - VERIFIED FUNCTIONAL
    
*   **GifCap_X.X.X_Linux_x64.flatpak**
    Flatpak package - VERIFIED FUNCTIONAL
    
*   **GifCap_X.X.X_Linux_x64.rpm**
    RPM installer (Fedora) - **NOT TESTED**
    
*   **GifCap_X.X.X_Linux_x64_Standalone.zip**
    Standalone Linux binary "gifcam" in a Zip file - VERIFIED FUNCTIONAL
    
*   **GifCap_X.X.X_MacOS_x64.zip**
    macOS app package in a Zip file. - **NOT TESTED**

*   **GifCap_X.X.X_Windows_x64_Installer.exe**
    Windows installer for program - **NOT TESTED**

*   **GifCap_X.X.X_Windows_x64_Standalone.zip**
    Standalone Windows .exe (portable) in a Zip file - **NOT TESTED**
