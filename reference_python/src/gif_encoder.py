"""
GIF Encoder - Export frames to animated GIF
"""

import imageio
from PIL import Image
import numpy as np


class GifEncoder:
    def __init__(self, frame_storage):
        self.frame_storage = frame_storage
    
    def export(self, output_path, color_mode="quantize", optimize=True):
        """
        Export frames to GIF
        
        Args:
            output_path: Path to save GIF file
            color_mode: Color reduction mode - "quantize", "256", "grayscale", "monochrome"
            optimize: Enable GIF optimization
        
        Returns:
            bool: True if successful
        """
        frame_count = self.frame_storage.get_frame_count()
        if frame_count == 0:
            print("Error: No frames to export")
            return False
        
        print(f"Exporting {frame_count} frames to {output_path}...")
        
        try:
            # Collect frames as RGB numpy arrays and delays
            frames = []
            durations = []
            
            for frame_img, delay_ms in self.frame_storage.get_all_frames():
                # Ensure RGB mode
                if frame_img.mode != "RGB":
                    frame_img = frame_img.convert("RGB")
                
                # Apply color transformations if needed
                if color_mode == "grayscale":
                    frame_img = frame_img.convert("L").convert("RGB")
                elif color_mode == "monochrome":
                    frame_img = frame_img.convert("1").convert("RGB")
                
                # Convert to numpy array as RGB
                frames.append(np.array(frame_img))
                # Convert milliseconds to seconds for imageio
                durations.append(delay_ms / 1000.0)
            
            # Write GIF using imageio - it will handle palette quantization globally
            imageio.mimsave(
                output_path,
                frames,
                format='GIF',
                duration=durations,
                loop=0,  # Infinite loop
            )
            
            print(f"GIF saved successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting GIF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_color_mode(self, image, mode):
        """
        Apply color reduction to image
        
        Args:
            image: PIL Image
            mode: Color reduction mode
        
        Returns:
            PIL Image with color reduction applied
        """
        # Ensure image is in RGB mode first
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        if mode == "quantize":
            # Intelligent quantization (PIL default)
            return image.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
        
        elif mode == "256":
            # Standard 256 color palette
            return image.convert("P", palette=Image.Palette.WEB)
        
        elif mode == "grayscale":
            # Convert to grayscale
            return image.convert("L")
        
        elif mode == "monochrome":
            # Convert to black and white
            return image.convert("1")
        
        else:
            # No conversion - return as RGB
            return image
    
    def estimate_size(self, color_mode="quantize"):
        """
        Estimate output file size (rough approximation)
        
        Returns:
            int: Estimated size in bytes
        """
        frame_count = self.frame_storage.get_frame_count()
        if frame_count == 0:
            return 0
        
        # Get a sample frame
        sample_frame, _ = next(self.frame_storage.get_all_frames())
        width, height = sample_frame.size
        
        # Rough estimation based on color mode
        if color_mode in ["quantize", "256"]:
            bytes_per_frame = width * height * 0.5  # Compressed estimate
        elif color_mode == "grayscale":
            bytes_per_frame = width * height * 0.3
        elif color_mode == "monochrome":
            bytes_per_frame = width * height * 0.1
        else:
            bytes_per_frame = width * height
        
        estimated_size = int(bytes_per_frame * frame_count)
        return estimated_size
