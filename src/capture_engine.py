"""
Capture Engine - Handle screen capture and frame comparison with hybrid X11/Wayland support
"""

import os
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PIL import Image, ImageChops
import mss
import numpy as np
from wayland_capture import WaylandPortalCapture
from cursor_capture import X11CursorCapture


class CaptureEngine(QObject):
    # Signals
    frame_captured = pyqtSignal(int)  # Emits frame number
    recording_stopped = pyqtSignal()
    
    def __init__(self, frame_storage):
        super().__init__()
        self.frame_storage = frame_storage
        
        # Detect session type and initialize appropriate capture
        self.session_type = self._detect_session()
        print(f"Detected session type: {self.session_type}")
        
        if self.session_type == 'wayland':
            self.wayland_capture = WaylandPortalCapture()
            if not self.wayland_capture.is_available:
                print("Warning: Wayland capture not available, falling back to X11")
                self.session_type = 'x11'
                self.sct = mss.mss()
        else:
            self.sct = mss.mss()
        
        # Cursor capture (X11 only for now, Wayland portal handles it)
        self.cursor_capture = X11CursorCapture() if self.session_type == 'x11' else None
        self.default_cursor = None
        if self.cursor_capture:
            self.default_cursor = self.cursor_capture.create_default_cursor()
        
        # Recording state
        self.is_recording = False
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._capture_frame)
        
        # Capture region (x, y, width, height)
        self.capture_region = None
        self.fps = 30
        self.capture_cursor = False
        
        # Frame comparison
        self.last_frame = None
        self.same_frame_delay = 0
        self.last_cursor_pos = None  # Track cursor position for change detection
    
    def _detect_session(self):
        """Detect if running on X11 or Wayland"""
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        xdg_session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        
        if wayland_display or xdg_session_type == 'wayland':
            return 'wayland'
        return 'x11'
    
    def set_capture_region(self, x, y, width, height):
        """Set the screen region to capture"""
        self.capture_region = {"top": int(y), "left": int(x), "width": int(width), "height": int(height)}
    
    def set_fps(self, fps):
        """Set capture frame rate"""
        self.fps = max(1, min(60, fps))  # Clamp between 1-60
    
    def start_recording(self):
        """Start capturing frames"""
        if not self.capture_region:
            print("Error: Capture region not set")
            return False
        
        self.is_recording = True
        self.last_frame = None
        self.same_frame_delay = 0
        
        # Calculate interval in milliseconds
        interval = int(1000 / self.fps)
        self.capture_timer.start(interval)
        print(f"Recording started at {self.fps} FPS")
        return True
    
    def stop_recording(self):
        """Stop capturing frames"""
        self.is_recording = False
        self.capture_timer.stop()
        
        # If there's accumulated delay from identical frames, add the last frame
        if self.same_frame_delay > 0 and self.last_frame is not None:
            self.frame_storage.add_frame(self.last_frame, self.same_frame_delay)
            self.frame_captured.emit(self.frame_storage.get_frame_count() - 1)
            self.same_frame_delay = 0
        
        print(f"Recording stopped. Total frames: {self.frame_storage.get_frame_count()}")
        self.recording_stopped.emit()
    
    def capture_single_frame(self):
        """Capture a single frame immediately"""
        if not self.capture_region:
            print("Error: Capture region not set")
            return False
        
        frame = self._grab_screen()
        if frame:
            delay = int(1000 / self.fps)  # Use FPS to determine delay
            frame_num = self.frame_storage.add_frame(frame, delay)
            self.frame_captured.emit(frame_num)
            return True
        return False
    
    def _capture_frame(self):
        """Capture a single frame and compare with previous"""
        frame = self._grab_screen()
        if frame is None:
            return
        
        delay_increment = int(1000 / self.fps)  # Milliseconds per frame
        
        # Get current cursor position if cursor capture is enabled
        current_cursor_pos = None
        if self.capture_cursor and self.cursor_capture:
            current_cursor_pos = self.cursor_capture.get_cursor_position()
        
        # Check if this frame is different from the last one OR cursor moved
        cursor_moved = False
        if self.capture_cursor and current_cursor_pos and self.last_cursor_pos:
            # Check if cursor moved significantly (more than a few pixels)
            dx = abs(current_cursor_pos[0] - self.last_cursor_pos[0])
            dy = abs(current_cursor_pos[1] - self.last_cursor_pos[1])
            cursor_moved = (dx > 2 or dy > 2)  # Threshold to avoid jitter
        
        if self.last_frame is not None:
            # Compare frames (without cursor, since it's composited after)
            if self._frames_identical(frame, self.last_frame) and not cursor_moved:
                # Same frame - accumulate delay
                self.same_frame_delay += delay_increment
                return
            else:
                # Different frame - save previous with accumulated delay
                if self.same_frame_delay > 0:
                    # Update delay for the last saved frame
                    self.frame_storage.update_last_frame_delay(self.same_frame_delay)
                    self.same_frame_delay = 0
        
        # Save new frame
        self.frame_storage.add_frame(frame, delay_increment)
        self.last_frame = frame.copy()
        self.last_cursor_pos = current_cursor_pos
        
        # Emit signal
        frame_num = self.frame_storage.get_frame_count()
        self.frame_captured.emit(frame_num)
        
        # Reset delay accumulator for next frame
        self.same_frame_delay = delay_increment
    
    def _grab_screen(self):
        """Grab the current screen region using appropriate method"""
        try:
            # Capture screen based on session type
            if self.session_type == 'wayland':
                img = self._grab_wayland()
            else:
                img = self._grab_x11()
            
            if img is None:
                return None
            
            # Composite cursor if enabled
            if self.capture_cursor:
                print(f"DEBUG: capture_cursor={self.capture_cursor}, cursor_capture={self.cursor_capture}, default_cursor={self.default_cursor is not None}")
                img = self._composite_cursor(img)
            else:
                print(f"DEBUG: Cursor compositing skipped (capture_cursor={self.capture_cursor})")
            
            return img
            
        except Exception as e:
            print(f"Error capturing screen: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _grab_x11(self):
        """Grab screen using mss (X11/XWayland)"""
        screenshot = self.sct.grab(self.capture_region)
        # mss returns BGRA format
        # The "BGRX" format string tells PIL to interpret it correctly as RGB
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        return img
    
    def _grab_wayland(self):
        """Grab screen using Wayland portal"""
        if not hasattr(self, 'wayland_capture') or not self.wayland_capture:
            return None
        
        return self.wayland_capture.grab_frame(
            self.capture_region['left'],
            self.capture_region['top'],
            self.capture_region['width'],
            self.capture_region['height']
        )
    
    def _composite_cursor(self, img):
        """Composite cursor onto the image"""
        if not self.cursor_capture or not self.default_cursor:
            return img
        
        # Get cursor position
        cursor_pos = self.cursor_capture.get_cursor_position()
        if not cursor_pos:
            return img
        
        x, y = cursor_pos
        
        # Convert to relative position within capture region
        rel_x = x - self.capture_region['left']
        rel_y = y - self.capture_region['top']
        
        # Check if cursor is within capture region
        if (rel_x < 0 or rel_y < 0 or 
            rel_x >= self.capture_region['width'] or 
            rel_y >= self.capture_region['height']):
            return img
        
        # Composite cursor onto image
        print(f"Compositing cursor at ({rel_x}, {rel_y})")
        img_with_cursor = img.copy()
        img_with_cursor.paste(self.default_cursor, (rel_x, rel_y), self.default_cursor)
        
        return img_with_cursor
    
    def _frames_identical(self, frame1, frame2, threshold=0.99):
        """
        Check if two frames are identical or nearly identical
        Uses pixel comparison with a threshold
        
        Args:
            frame1, frame2: PIL Image objects
            threshold: Similarity threshold (0-1), where 1.0 means exactly identical
        
        Returns:
            bool: True if frames are considered identical
        """
        try:
            # Quick size check
            if frame1.size != frame2.size:
                return False
            
            # Convert to numpy arrays for comparison
            arr1 = np.array(frame1)
            arr2 = np.array(frame2)
            
            # Calculate difference
            diff = np.abs(arr1.astype(int) - arr2.astype(int))
            
            # Calculate similarity (percentage of identical pixels)
            total_pixels = diff.size
            identical_pixels = np.sum(diff == 0)
            similarity = identical_pixels / total_pixels
            
            return similarity >= threshold
            
        except Exception as e:
            print(f"Error comparing frames: {e}")
            return False
