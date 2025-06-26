"""
Enhanced Live Preview System
Provides advanced preview capabilities with hot reload, multiple device simulation,
and developer tools integration.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, 
    QSplitter, QTabWidget, QTextEdit, QSlider, QLabel, QCheckBox,
    QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

class FileWatcher(QThread, FileSystemEventHandler):
    """File system watcher for hot reload functionality"""
    file_changed = pyqtSignal(str)
    
    def __init__(self, watch_path: str):
        QThread.__init__(self)
        FileSystemEventHandler.__init__(self)
        self.watch_path = watch_path
        self.observer = Observer()
        self.last_modified = {}
        
    def run(self):
        self.observer.schedule(self, self.watch_path, recursive=True)
        self.observer.start()
        self.exec()
        
    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            # Throttle file change events
            current_time = time.time()
            if file_path not in self.last_modified or current_time - self.last_modified[file_path] > 0.5:
                self.last_modified[file_path] = current_time
                if any(file_path.endswith(ext) for ext in ['.html', '.css', '.js', '.json']):
                    self.file_changed.emit(file_path)
    
    def stop_watching(self):
        self.observer.stop()
        self.quit()

class DevicePresets:
    """Device presets for responsive preview"""
    DEVICES = {
        'Desktop': {'width': 1920, 'height': 1080, 'dpr': 1.0},
        'Laptop': {'width': 1366, 'height': 768, 'dpr': 1.0},
        'iPad Pro': {'width': 1024, 'height': 1366, 'dpr': 2.0},
        'iPad': {'width': 768, 'height': 1024, 'dpr': 2.0},
        'iPhone 14 Pro': {'width': 393, 'height': 852, 'dpr': 3.0},
        'iPhone 14': {'width': 390, 'height': 844, 'dpr': 3.0},
        'Samsung Galaxy S21': {'width': 384, 'height': 854, 'dpr': 2.75},
        'Custom': {'width': 800, 'height': 600, 'dpr': 1.0}
    }

class EnhancedPreviewPanel(QWidget):
    """Enhanced preview panel with hot reload and developer tools"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_watcher = None
        self.current_project_path = None
        self.auto_refresh_enabled = True
        self.current_zoom = 100
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Controls Section
        self.create_controls()
        layout.addWidget(self.controls_group)
        
        # Main Preview Area
        if HAS_WEBENGINE:
            self.create_preview_area()
            layout.addWidget(self.preview_splitter)
        else:
            no_engine_label = QLabel("WebEngine not available. Install PyQt6-WebEngine for preview functionality.")
            no_engine_label.setStyleSheet("color: red; padding: 20px; text-align: center;")
            layout.addWidget(no_engine_label)
    
    def create_controls(self):
        """Create the controls section"""
        self.controls_group = QGroupBox("Live Preview Controls")
        controls_layout = QVBoxLayout(self.controls_group)
        
        # First row: Device and Auto-refresh
        row1 = QHBoxLayout()
        
        # Device selector
        row1.addWidget(QLabel("Device:"))
        self.device_combo = QComboBox()
        self.device_combo.addItems(list(DevicePresets.DEVICES.keys()))
        self.device_combo.setCurrentText("Desktop")
        self.device_combo.currentTextChanged.connect(self.on_device_changed)
        row1.addWidget(self.device_combo)
        
        # Auto-refresh toggle
        self.auto_refresh_checkbox = QCheckBox("Auto Refresh")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        row1.addWidget(self.auto_refresh_checkbox)
        
        # Manual refresh button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.manual_refresh)
        row1.addWidget(self.refresh_btn)
        
        row1.addStretch()
        controls_layout.addLayout(row1)
        
        # Second row: Zoom and custom dimensions
        row2 = QHBoxLayout()
        
        # Zoom control
        row2.addWidget(QLabel("Zoom:"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        row2.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(40)
        row2.addWidget(self.zoom_label)
        
        # Custom dimensions (only shown when Custom device is selected)
        row2.addWidget(QLabel("W:"))
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(200, 4000)
        self.width_spinbox.setValue(800)
        self.width_spinbox.valueChanged.connect(self.on_custom_size_changed)
        row2.addWidget(self.width_spinbox)
        
        row2.addWidget(QLabel("H:"))
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(200, 4000)
        self.height_spinbox.setValue(600)
        self.height_spinbox.valueChanged.connect(self.on_custom_size_changed)
        row2.addWidget(self.height_spinbox)
        
        row2.addStretch()
        controls_layout.addLayout(row2)
        
        # Third row: Developer tools
        row3 = QHBoxLayout()
        
        self.dev_tools_btn = QPushButton("🔧 Developer Tools")
        self.dev_tools_btn.clicked.connect(self.toggle_dev_tools)
        row3.addWidget(self.dev_tools_btn)
        
        self.fullscreen_btn = QPushButton("⛶ Fullscreen")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        row3.addWidget(self.fullscreen_btn)
        
        row3.addStretch()
        controls_layout.addLayout(row3)
        
        # Style the controls
        self.controls_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
    
    def create_preview_area(self):
        """Create the preview area with optional developer tools"""
        self.preview_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Main preview
        self.web_view = QWebEngineView()
        self.preview_splitter.addWidget(self.web_view)
        
        # Developer tools (initially hidden)
        self.dev_tools_container = QTabWidget()
        self.dev_tools_container.hide()
        
        # Console tab
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Consolas", 10))
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
            }
        """)
        self.dev_tools_container.addTab(self.console_output, "Console")
        
        # Network tab
        self.network_output = QTextEdit()
        self.network_output.setReadOnly(True)
        self.network_output.setFont(QFont("Consolas", 10))
        self.network_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
            }
        """)
        self.dev_tools_container.addTab(self.network_output, "Network")
        
        self.preview_splitter.addWidget(self.dev_tools_container)
        self.preview_splitter.setSizes([700, 200])
    
    def set_project_path(self, path: str):
        """Set the project path and start file watching"""
        self.current_project_path = path
        
        # Stop existing watcher
        if self.file_watcher:
            self.file_watcher.stop_watching()
            
        # Start new watcher
        if path and os.path.exists(path):
            self.file_watcher = FileWatcher(path)
            self.file_watcher.file_changed.connect(self.on_file_changed)
            self.file_watcher.start()
    
    @pyqtSlot(str)
    def on_file_changed(self, file_path: str):
        """Handle file change events"""
        if self.auto_refresh_enabled:
            # Add delay to avoid rapid refreshes
            QTimer.singleShot(500, self.refresh_preview)
            
        # Log to console
        self.log_to_console(f"File changed: {os.path.basename(file_path)}")
    
    def on_device_changed(self, device_name: str):
        """Handle device selection change"""
        if device_name in DevicePresets.DEVICES:
            device = DevicePresets.DEVICES[device_name]
            
            # Show/hide custom dimensions
            custom_visible = device_name == "Custom"
            self.width_spinbox.setVisible(custom_visible)
            self.height_spinbox.setVisible(custom_visible)
            
            if not custom_visible:
                self.width_spinbox.setValue(device['width'])
                self.height_spinbox.setValue(device['height'])
            
            self.apply_device_settings(device)
    
    def on_custom_size_changed(self):
        """Handle custom size change"""
        if self.device_combo.currentText() == "Custom":
            device = {
                'width': self.width_spinbox.value(),
                'height': self.height_spinbox.value(),
                'dpr': 1.0
            }
            self.apply_device_settings(device)
    
    def apply_device_settings(self, device: Dict):
        """Apply device settings to the preview"""
        if HAS_WEBENGINE:
            width = int(device['width'] * self.current_zoom / 100)
            height = int(device['height'] * self.current_zoom / 100)
            self.web_view.setFixedSize(width, height)
    
    def on_zoom_changed(self, value: int):
        """Handle zoom change"""
        self.current_zoom = value
        self.zoom_label.setText(f"{value}%")
        
        # Reapply current device settings with new zoom
        current_device = self.device_combo.currentText()
        if current_device in DevicePresets.DEVICES:
            self.apply_device_settings(DevicePresets.DEVICES[current_device])
    
    def toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh functionality"""
        self.auto_refresh_enabled = enabled
        self.log_to_console(f"Auto-refresh {'enabled' if enabled else 'disabled'}")
    
    def manual_refresh(self):
        """Manually refresh the preview"""
        self.refresh_preview()
        self.log_to_console("Manual refresh triggered")
    
    def refresh_preview(self):
        """Refresh the preview content"""
        if HAS_WEBENGINE and self.current_project_path:
            # Find the main HTML file
            html_files = ['index.html', 'main.html', 'app.html']
            for html_file in html_files:
                html_path = os.path.join(self.current_project_path, html_file)
                if os.path.exists(html_path):
                    self.web_view.load(QUrl.fromLocalFile(html_path))
                    break
    
    def toggle_dev_tools(self):
        """Toggle developer tools visibility"""
        if self.dev_tools_container.isVisible():
            self.dev_tools_container.hide()
            self.dev_tools_btn.setText("🔧 Developer Tools")
        else:
            self.dev_tools_container.show()
            self.dev_tools_btn.setText("🔧 Hide Dev Tools")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        # This would be implemented based on the parent window structure
        self.log_to_console("Fullscreen toggle - implementation needed")
    
    def log_to_console(self, message: str):
        """Log a message to the console"""
        if hasattr(self, 'console_output'):
            timestamp = time.strftime("%H:%M:%S")
            self.console_output.append(f"[{timestamp}] {message}")
    
    def load_url(self, url: QUrl):
        """Load a URL in the preview"""
        if HAS_WEBENGINE:
            self.web_view.load(url)
            self.log_to_console(f"Loading: {url.toString()}")
    
    def closeEvent(self, event):
        """Clean up when closing"""
        if self.file_watcher:
            self.file_watcher.stop_watching()
        super().closeEvent(event)
