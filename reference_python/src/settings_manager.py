"""
Settings Manager - Handle configuration persistence
"""

import os
import json
from pathlib import Path


class SettingsManager:
    def __init__(self):
        # Use XDG config directory
        config_dir = Path.home() / ".config" / "gifcap"
        config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = config_dir / "settings.json"
        
        # Default settings
        self.defaults = {
            "fps": 30,
            "window_width": 400,
            "window_height": 300,
            "last_save_dir": str(Path.home()),
            "capture_cursor": False,
            "storage_mode": "disk"  # "disk" or "ram"
        }
        
        self.settings = self.load()
    
    def load(self):
        """Load settings from disk or return defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    return {**self.defaults, **loaded}
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save(self):
        """Save current settings to disk"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default if default is not None else self.defaults.get(key))
    
    def set(self, key, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save()


# Global settings instance
settings = SettingsManager()
