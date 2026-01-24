#!/usr/bin/env python3
"""
GifCap - Linux Screen Recorder for GIFs
Main application entry point
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from recorder_window import RecorderWindow


def main():
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("GifCap")
    app.setOrganizationName("GifCap")
    
    # Create and show the main recorder window
    window = RecorderWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
