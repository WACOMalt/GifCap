"""
Editor Window - Frame strip editor with right-click operations
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                              QLabel, QPushButton, QMenu, QDialog, QSpinBox,
                              QDialogButtonBox, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor
from PIL import Image
import numpy as np


class DelayEntryDialog(QDialog):
    """Dialog for entering frame delay via keyboard"""
    
    def __init__(self, current_delay, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Frame Delay")
        self.setup_ui(current_delay)
    
    def setup_ui(self, current_delay):
        layout = QVBoxLayout()
        
        # Delay spinbox
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Delay (ms):")
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(10, 10000)
        self.delay_spinbox.setValue(current_delay)
        self.delay_spinbox.setSingleStep(10)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_spinbox)
        layout.addLayout(delay_layout)
        
        # Apply to all checkbox
        self.apply_all_checkbox = QCheckBox("Apply to all frames")
        layout.addWidget(self.apply_all_checkbox)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_delay(self):
        """Get the entered delay value"""
        return self.delay_spinbox.value()
    
    def apply_to_all(self):
        """Check if delay should be applied to all frames"""
        return self.apply_all_checkbox.isChecked()


class FrameThumbnail(QLabel):
    """Individual frame thumbnail with number label"""
    
    clicked = pyqtSignal(int)  # Emits frame number
    right_clicked = pyqtSignal(int, object)  # Emits frame number and position
    
    def __init__(self, frame_num, image, delay, thumbnail_size=120):
        super().__init__()
        self.frame_num = frame_num
        self.delay = delay
        self.thumbnail_size = thumbnail_size
        
        # Set up the thumbnail
        self.setFixedSize(thumbnail_size + 20, thumbnail_size + 40)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #3d3d3d;
                border: 2px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QLabel:hover {
                border-color: #00ff00;
            }
        """)
        
        # Create thumbnail from PIL Image
        self.update_thumbnail(image, delay)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    
    def update_thumbnail(self, image, delay):
        """Update the thumbnail image and delay label"""
        self.delay = delay
        
        # Resize image to thumbnail size
        img = image.copy()
        img.thumbnail((self.thumbnail_size, self.thumbnail_size), Image.Resampling.LANCZOS)
        
        # Convert PIL Image to QPixmap with proper stride
        img_rgb = img.convert("RGB")
        width, height = img_rgb.size
        data = img_rgb.tobytes("raw", "RGB")
        bytes_per_line = width * 3  # RGB = 3 bytes per pixel
        qimg = QImage(data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        
        # Create a composite with frame number and delay
        composite = QPixmap(self.thumbnail_size + 10, self.thumbnail_size + 30)
        composite.fill(QColor("#3d3d3d"))
        
        painter = QPainter(composite)
        
        # Draw image centered
        x = (composite.width() - pixmap.width()) // 2
        y = 5
        painter.drawPixmap(x, y, pixmap)
        
        # Draw frame number and delay
        painter.setPen(QColor("#ffffff"))
        info_text = f"#{self.frame_num} ({self.delay}ms)"
        painter.drawText(0, pixmap.height() + 20, composite.width(), 20, 
                        Qt.AlignmentFlag.AlignCenter, info_text)
        
        painter.end()
        
        self.setPixmap(composite)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.frame_num)
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(self.frame_num, event.globalPosition())


class EditorWindow(QWidget):
    """Frame editor with horizontal frame strip and editing operations"""
    
    frames_modified = pyqtSignal()  # Emitted when frames are modified
    
    def __init__(self, frame_storage):
        super().__init__()
        self.frame_storage = frame_storage
        self.thumbnails = []
        
        self.setWindowTitle("GifCap Editor")
        self.resize(800, 250)
        
        self.init_ui()
        self.load_frames()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Title bar
        title_layout = QHBoxLayout()
        title_label = QLabel("Frame Editor")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(close_btn)
        layout.addLayout(title_layout)
        
        # Scroll area for frames
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Frame container
        self.frame_container = QWidget()
        self.frame_layout = QHBoxLayout()
        self.frame_layout.setSpacing(10)
        self.frame_layout.setContentsMargins(10, 10, 10, 10)
        self.frame_container.setLayout(self.frame_layout)
        
        scroll.setWidget(self.frame_container)
        layout.addWidget(scroll)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QScrollArea {
                border: 1px solid #555555;
            }
        """)
        
        self.setLayout(layout)
    
    def load_frames(self):
        """Load all frames as thumbnails"""
        frame_count = self.frame_storage.get_frame_count()
        
        for i in range(frame_count):
            frame_img = self.frame_storage.get_frame(i)
            delay = self.frame_storage.get_delay(i)
            
            thumbnail = FrameThumbnail(i, frame_img, delay)
            thumbnail.clicked.connect(self.on_frame_clicked)
            thumbnail.right_clicked.connect(self.on_frame_right_clicked)
            
            self.thumbnails.append(thumbnail)
            self.frame_layout.addWidget(thumbnail)
        
        self.frame_layout.addStretch()
        self.update_info()
    
    def update_info(self):
        """Update the info label"""
        frame_count = self.frame_storage.get_frame_count()
        self.info_label.setText(f"Total frames: {frame_count}")
    
    def on_frame_clicked(self, frame_num):
        """Handle frame click"""
        print(f"Frame {frame_num} clicked")
    
    def on_frame_right_clicked(self, frame_num, position):
        """Handle frame right-click - show context menu"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #4d4d4d;
            }
        """)
        
        # Menu actions
        delete_action = menu.addAction(f"Delete frame #{frame_num}")
        delete_to_start_action = menu.addAction("Delete from frame to beginning")
        delete_to_end_action = menu.addAction("Delete from frame to end")
        delete_even_action = menu.addAction("Delete even-numbered frames")
        menu.addSeparator()
        delay_action = menu.addAction("Keyboard entry (frame delay)...")
        
        # Execute menu
        action = menu.exec(position.toPoint())
        
        if action == delete_action:
            self.delete_frame(frame_num)
        elif action == delete_to_start_action:
            self.delete_to_beginning(frame_num)
        elif action == delete_to_end_action:
            self.delete_to_end(frame_num)
        elif action == delete_even_action:
            self.delete_even_frames()
        elif action == delay_action:
            self.show_delay_dialog(frame_num)
    
    def delete_frame(self, frame_num):
        """Delete a single frame"""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete frame #{frame_num}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.frame_storage.delete_frame(frame_num)
            self.refresh_display()
            self.frames_modified.emit()
    
    def delete_to_beginning(self, frame_num):
        """Delete all frames from beginning to this frame (inclusive)"""
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete frames 0 to {frame_num} ({frame_num + 1} frames)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            frames_to_delete = list(range(frame_num + 1))
            self.frame_storage.delete_frames(frames_to_delete)
            self.refresh_display()
            self.frames_modified.emit()
    
    def delete_to_end(self, frame_num):
        """Delete all frames from this frame to end (inclusive)"""
        total_frames = self.frame_storage.get_frame_count()
        count = total_frames - frame_num
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete frames {frame_num} to {total_frames - 1} ({count} frames)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            frames_to_delete = list(range(frame_num, total_frames))
            self.frame_storage.delete_frames(frames_to_delete)
            self.refresh_display()
            self.frames_modified.emit()
    
    def delete_even_frames(self):
        """Delete all even-numbered frames"""
        total_frames = self.frame_storage.get_frame_count()
        even_frames = [i for i in range(total_frames) if i % 2 == 0]
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete all even-numbered frames ({len(even_frames)} frames)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.frame_storage.delete_frames(even_frames)
            self.refresh_display()
            self.frames_modified.emit()
    
    def show_delay_dialog(self, frame_num):
        """Show dialog for entering frame delay"""
        current_delay = self.frame_storage.get_delay(frame_num)
        dialog = DelayEntryDialog(current_delay, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_delay = dialog.get_delay()
            
            if dialog.apply_to_all():
                # Apply to all frames
                for i in range(self.frame_storage.get_frame_count()):
                    self.frame_storage.set_delay(i, new_delay)
                self.refresh_display()
            else:
                # Apply to single frame
                self.frame_storage.set_delay(frame_num, new_delay)
                # Just update this thumbnail
                frame_img = self.frame_storage.get_frame(frame_num)
                if frame_num < len(self.thumbnails):
                    self.thumbnails[frame_num].update_thumbnail(frame_img, new_delay)
            
            self.frames_modified.emit()
    
    def refresh_display(self):
        """Refresh the entire frame display"""
        # Clear existing thumbnails
        for thumbnail in self.thumbnails:
            self.frame_layout.removeWidget(thumbnail)
            thumbnail.deleteLater()
        
        self.thumbnails.clear()
        
        # Reload frames
        self.load_frames()
