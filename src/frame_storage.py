"""
Frame Storage - Manage captured frames on disk or in RAM
"""

import os
import shutil
import json
from pathlib import Path
from PIL import Image
import tempfile
import uuid


class FrameStorage:
    def __init__(self, storage_mode="disk"):
        self.storage_mode = storage_mode
        self.session_id = str(uuid.uuid4())[:8]
        self.frames = []  # List of frame metadata
        self.frame_dir = None
        
        if storage_mode == "disk":
            # Create temporary directory for frames
            self.frame_dir = Path(tempfile.gettempdir()) / f"gifcap_frames_{self.session_id}"
            self.frame_dir.mkdir(parents=True, exist_ok=True)
            print(f"Frame storage: {self.frame_dir}")
        else:
            # RAM mode - store PIL Images directly
            self.ram_frames = []
    
    def add_frame(self, image, delay=100):
        """
        Add a frame to storage
        
        Args:
            image: PIL Image object
            delay: Frame delay in milliseconds
        """
        frame_num = len(self.frames)
        
        if self.storage_mode == "disk":
            # Save to disk
            frame_path = self.frame_dir / f"frame_{frame_num:05d}.png"
            image.save(frame_path, "PNG")
            
            metadata = {
                "frame_num": frame_num,
                "delay": delay,
                "path": str(frame_path)
            }
        else:
            # Store in RAM
            self.ram_frames.append(image.copy())
            metadata = {
                "frame_num": frame_num,
                "delay": delay,
                "path": None
            }
        
        self.frames.append(metadata)
        return frame_num
    
    def get_frame(self, frame_num):
        """Get a frame by number"""
        if frame_num >= len(self.frames):
            return None
        
        if self.storage_mode == "disk":
            path = self.frames[frame_num]["path"]
            return Image.open(path)
        else:
            return self.ram_frames[frame_num]
    
    def get_frame_count(self):
        """Return total number of frames"""
        return len(self.frames)
    
    def get_delay(self, frame_num):
        """Get delay for a specific frame"""
        if frame_num < len(self.frames):
            return self.frames[frame_num]["delay"]
        return 100  # Default
    
    def set_delay(self, frame_num, delay):
        """Set delay for a specific frame"""
        if frame_num < len(self.frames):
            self.frames[frame_num]["delay"] = delay
    
    def update_last_frame_delay(self, delay):
        """Update delay for the last frame in storage"""
        if len(self.frames) > 0:
            self.frames[-1]["delay"] = delay
    
    def delete_frame(self, frame_num):
        """Delete a specific frame"""
        if frame_num >= len(self.frames):
            return False
        
        if self.storage_mode == "disk":
            # Delete file
            path = Path(self.frames[frame_num]["path"])
            if path.exists():
                path.unlink()
        else:
            # Remove from RAM
            del self.ram_frames[frame_num]
        
        # Remove metadata
        del self.frames[frame_num]
        
        # Renumber remaining frames
        for i, frame in enumerate(self.frames):
            frame["frame_num"] = i
        
        return True
    
    def delete_frames(self, frame_nums):
        """Delete multiple frames (indices should be sorted descending)"""
        for frame_num in sorted(frame_nums, reverse=True):
            self.delete_frame(frame_num)
    
    def get_all_frames(self):
        """Generator that yields (frame_image, delay) tuples"""
        for i in range(len(self.frames)):
            yield self.get_frame(i), self.frames[i]["delay"]
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.storage_mode == "disk" and self.frame_dir and self.frame_dir.exists():
            try:
                shutil.rmtree(self.frame_dir)
                print(f"Cleaned up frame storage: {self.frame_dir}")
            except Exception as e:
                print(f"Error cleaning up frames: {e}")
        
        self.frames.clear()
        if self.storage_mode == "ram":
            self.ram_frames.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.cleanup()
