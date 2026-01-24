"""
Recorder Window - Main window with transparent cutout and controls
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QLabel, QSpinBox, QFileDialog, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QRegion, QPainter, QColor, QPen
from settings_manager import settings
from frame_storage import FrameStorage
from capture_engine import CaptureEngine
from gif_encoder import GifEncoder
from editor_window import EditorWindow


class RecorderWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window setup - allow normal window decorations for resizing
        self.setWindowTitle("GifCap")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Load settings
        width = settings.get("window_width", 400)
        height = settings.get("window_height", 300)
        self.resize(width, height)
        
        # Recording state
        self.frame_storage = FrameStorage(storage_mode=settings.get("storage_mode", "disk"))
        self.capture_engine = CaptureEngine(self.frame_storage)
        self.gif_encoder = GifEncoder(self.frame_storage)
        self.editor_window = None
        
        # Connect signals
        self.capture_engine.frame_captured.connect(self.on_frame_captured)
        self.capture_engine.recording_stopped.connect(self.on_recording_stopped)
        
        # UI state
        self.is_recording = False
        self.frame_count = 0
        
        # Mouse dragging not needed - window manager handles it
        
        # Initialize UI
        self.init_ui()
        
        # Set FPS from settings
        fps = settings.get("fps", 30)
        self.fps_spinbox.setValue(fps)
        self.capture_engine.set_fps(fps)
        
        # Set cursor capture from settings (default enabled)
        capture_cursor = settings.get("capture_cursor", True)
        self.cursor_checkbox.setChecked(capture_cursor)
        self.capture_engine.capture_cursor = capture_cursor
    
    def init_ui(self):
        """Initialize the user interface"""
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Cutout region (transparent - shows desktop underneath)
        self.cutout_widget = QWidget()
        self.cutout_widget.setStyleSheet("background: transparent;")
        
        # Add cutout with stretch factor (takes remaining space)
        main_layout.addWidget(self.cutout_widget, stretch=1)
        
        # Control panel (right side) - fixed width
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, stretch=0)
        
        self.setLayout(main_layout)
        
        # Make window transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Update capture region
        self.update_capture_region()
        
        # Set up window mask to allow clicking through cutout
        # This will be updated in resizeEvent
        self.update_window_mask()
    
    def update_window_mask(self):
        """Set window mask to make cutout area click-through"""
        from PyQt6.QtGui import QRegion
        
        # Create a region that only covers the control panel (right side)
        # This allows clicks to pass through the cutout area
        control_panel_x = self.cutout_widget.width()
        control_panel_rect = QRegion(
            control_panel_x, 0,
            self.width() - control_panel_x, self.height()
        )
        
        # Set the mask - only the control panel receives input
        self.setMask(control_panel_rect)
    
    def create_control_panel(self):
        """Create the right-hand control panel"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QPushButton#rec_button_recording {
                background-color: #c0392b;
            }
            QPushButton#rec_button_recording:hover {
                background-color: #e74c3c;
            }
            QSpinBox {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                min-height: 25px;
            }
            QLabel {
                font-size: 11px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("GifCap")
        title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # FPS control
        fps_layout = QHBoxLayout()
        fps_label = QLabel("FPS:")
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 60)
        self.fps_spinbox.setValue(30)
        self.fps_spinbox.valueChanged.connect(self.on_fps_changed)
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(self.fps_spinbox)
        layout.addLayout(fps_layout)
        
        # Cursor capture checkbox (composites our own cursor)
        self.cursor_checkbox = QCheckBox("Capture\nCursor")
        self.cursor_checkbox.setChecked(True)  # Default enabled
        self.cursor_checkbox.stateChanged.connect(self.on_cursor_changed)
        self.cursor_checkbox.setStyleSheet("font-size: 10px;")
        layout.addWidget(self.cursor_checkbox)
        
        # Rec button
        self.rec_button = QPushButton("Rec")
        self.rec_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.rec_button)
        
        # Frame button
        frame_button = QPushButton("Frame")
        frame_button.clicked.connect(self.capture_frame)
        layout.addWidget(frame_button)
        
        # Edit button
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.open_editor)
        self.edit_button.setEnabled(False)
        layout.addWidget(self.edit_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_gif)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        
        # Frame counter
        self.frame_counter_label = QLabel("Frames: 0")
        self.frame_counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.frame_counter_label)
        
        layout.addStretch()
        
        panel.setLayout(layout)
        panel.setFixedWidth(120)
        
        return panel
    
    def resizeEvent(self, event):
        """Handle window resize to update capture region"""
        super().resizeEvent(event)
        self.update_capture_region()
        self.update_window_mask()  # Update click-through region



    
    def update_capture_region(self):
        """Update the screen capture region based on cutout position"""
        # Get the global position and size of the cutout widget
        cutout_global_pos = self.cutout_widget.mapToGlobal(self.cutout_widget.rect().topLeft())
        cutout_size = self.cutout_widget.size()
        
        self.capture_engine.set_capture_region(
            cutout_global_pos.x(),
            cutout_global_pos.y(),
            cutout_size.width(),
            cutout_size.height()
        )
    
    def on_fps_changed(self, value):
        """Handle FPS spinbox change"""
        self.capture_engine.set_fps(value)
        settings.set("fps", value)
    
    def on_cursor_changed(self, state):
        """Handle cursor capture checkbox change"""
        capture_cursor = (state == Qt.CheckState.Checked.value)
        self.capture_engine.capture_cursor = capture_cursor
        settings.set("capture_cursor", capture_cursor)
        print(f"Cursor capture {'enabled' if capture_cursor else 'disabled'}")
    
    def moveEvent(self, event):
        """Handle window move to update capture region"""
        super().moveEvent(event)
        # Update capture region when window is moved
        self.update_capture_region()
        self.update_window_mask()  # Update click-through region


    
    def toggle_recording(self):
        """Toggle recording on/off"""
        if self.is_recording:
            # Stop recording
            self.capture_engine.stop_recording()
            self.is_recording = False
            self.rec_button.setText("Rec")
            self.rec_button.setObjectName("")
            self.rec_button.setStyleSheet(self.rec_button.styleSheet())
        else:
            # Start recording
            self.update_capture_region()
            if self.capture_engine.start_recording():
                self.is_recording = True
                self.rec_button.setText("Stop")
                self.rec_button.setObjectName("rec_button_recording")
                self.rec_button.setStyleSheet(self.rec_button.styleSheet())
    
    def capture_frame(self):
        """Capture a single frame"""
        self.update_capture_region()
        self.capture_engine.capture_single_frame()
    
    def on_frame_captured(self, frame_num):
        """Handle frame captured signal"""
        self.frame_count = self.frame_storage.get_frame_count()
        self.frame_counter_label.setText(f"Frames: {self.frame_count}")
        self.edit_button.setEnabled(self.frame_count > 0)
        self.save_button.setEnabled(self.frame_count > 0)
    
    def on_recording_stopped(self):
        """Handle recording stopped signal"""
        self.frame_count = self.frame_storage.get_frame_count()
        self.frame_counter_label.setText(f"Frames: {self.frame_count}")
    
    def open_editor(self):
        """Open the frame editor window"""
        if self.frame_count == 0:
            return
        
        self.editor_window = EditorWindow(self.frame_storage)
        self.editor_window.frames_modified.connect(self.on_frames_modified)
        self.editor_window.show()
    
    def on_frames_modified(self):
        """Handle frames modified in editor"""
        self.frame_count = self.frame_storage.get_frame_count()
        self.frame_counter_label.setText(f"Frames: {self.frame_count}")
        self.edit_button.setEnabled(self.frame_count > 0)
        self.save_button.setEnabled(self.frame_count > 0)
    
    def save_gif(self):
        """Export frames to GIF"""
        if self.frame_count == 0:
            return
        
        # File dialog
        default_dir = settings.get("last_save_dir", "")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save GIF",
            default_dir + "/recording.gif",
            "GIF Files (*.gif)"
        )
        
        if file_path:
            # Save directory for next time
            import os
            settings.set("last_save_dir", os.path.dirname(file_path))
            
            # Export GIF
            success = self.gif_encoder.export(file_path, color_mode="quantize")
            
            if success:
                QMessageBox.information(self, "Success", f"GIF saved to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save GIF")
    
    def closeEvent(self, event):
        """Handle window close"""
        # Save window size
        settings.set("window_width", self.width())
        settings.set("window_height", self.height())
        
        # Cleanup
        self.frame_storage.cleanup()
        
        event.accept()
