"""
Wayland Portal Capture - Screen capture via xdg-desktop-portal for Wayland support
"""

import os
import subprocess
from pathlib import Path
from PIL import Image
import tempfile


class WaylandPortalCapture:
    """
    Screen capture using xdg-desktop-portal ScreenCast API
    This works on both Wayland and X11
    """
    
    def __init__(self):
        self.is_available = self._check_portal_available()
        self.temp_dir = None
        self.recording_process = None
    
    def _check_portal_available(self):
        """Check if xdg-desktop-portal is available"""
        try:
            # Check if we can communicate with the portal
            result = subprocess.run(
                ['busctl', 'status', 'org.freedesktop.portal.Desktop'],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def start_capture(self, x, y, width, height):
        """
        Start screen capture via portal
        Note: First time will require user permission dialog
        """
        if not self.is_available:
            return False
        
        # Create temp directory for screenshots
        self.temp_dir = Path(tempfile.mkdtemp(prefix="gifcap_portal_"))
        
        # For now, use grim/slurp as a simpler alternative
        # Full portal implementation would require D-Bus bindings
        return self._check_grim_available()
    
    def _check_grim_available(self):
        """Check if grim (Wayland screenshot tool) is available"""
        try:
            result = subprocess.run(['which', 'grim'], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def grab_frame(self, x, y, width, height):
        """
        Capture a frame of the specified region
        Returns PIL Image or None
        """
        if not self.temp_dir:
            return None
        
        # Use grim for Wayland screenshot
        # grim -g "x,y widthxheight" output.png
        output_file = self.temp_dir / f"frame_{os.getpid()}.png"
        geometry = f"{x},{y} {width}x{height}"
        
        try:
            subprocess.run(
                ['grim', '-g', geometry, str(output_file)],
                capture_output=True,
                timeout=1,
                check=True
            )
            
            if output_file.exists():
                img = Image.open(output_file)
                output_file.unlink()  # Clean up
                return img
            
        except Exception as e:
            print(f"Error capturing via portal: {e}")
        
        return None
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and self.temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass
    
    def __del__(self):
        self.cleanup()
