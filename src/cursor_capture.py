"""
X11 Cursor Capture - Get cursor image and position for compositing
"""

from PyQt6.QtGui import QCursor
from PIL import Image, ImageDraw


class X11CursorCapture:
    """Capture cursor information for compositing (works on all platforms via Qt)"""
    
    def __init__(self):
        self.available = True  # Always available via Qt
    
    def get_cursor_position(self):
        """
        Get cursor position using Qt (cross-platform, no dependencies)
        Returns (x, y) tuple
        """
        try:
            pos = QCursor.pos()
            return (pos.x(), pos.y())
        except Exception as e:
            print(f"Error getting cursor position: {e}")
            return None
    
    def get_cursor_image(self):
        """
        Get the current cursor image
        For now, returns None and we use default cursor
        Future: Could extract themed cursor via platform-specific APIs
        """
        return None
    
    def create_default_cursor(self):
        """Create a simple default cursor image (white arrow with black outline)"""
        # Create 24x24 cursor
        cursor = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
        draw = ImageDraw.Draw(cursor)
        
        # Draw arrow shape
        arrow = [(0, 0), (0, 16), (4, 12), (7, 18), (9, 17), (6, 10), (12, 10)]
        
        # Black outline
        draw.polygon(arrow, fill=(0, 0, 0, 255), outline=(0, 0, 0, 255))
        
        # White fill (offset by 1 pixel)
        arrow_inner = [(1, 1), (1, 14), (4, 11), (7, 16), (8, 15), (5, 9), (10, 9)]
        draw.polygon(arrow_inner, fill=(255, 255, 255, 255))
        
        return cursor

