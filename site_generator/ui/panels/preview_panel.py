
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import QEvent, Qt, QUrl

from .fullscreen_preview_window import FullscreenPreviewWindow

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.fullscreen_window = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if HAS_WEBENGINE:
            preview_controls = QHBoxLayout()
            preview_controls.addWidget(QLabel('Preview:'))
            
            self.preview_size = QComboBox()
            self.preview_size.addItems(['Desktop', 'Tablet', 'Mobile'])
            self.preview_size.setStyleSheet("""
                QComboBox {
                    padding: 5px;
                    border: 1px solid #666;
                    border-radius: 3px;
                    background: white;
                }
            """)
            preview_controls.addWidget(self.preview_size)
            
            self.refresh_btn = QPushButton('↻ Atualizar')
            self.refresh_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a4a4a;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
            """)
            preview_controls.addWidget(self.refresh_btn)

            self.fullscreen_btn = QPushButton('⛶ Fullscreen')
            self.fullscreen_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a4a4a;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
            """)
            preview_controls.addWidget(self.fullscreen_btn)

            preview_controls.addStretch()
            
            layout.addLayout(preview_controls)

            self.site_preview = QWebEngineView()
            self.site_preview.setMinimumWidth(375)
            self.site_preview.setStyleSheet("""
                QWebEngineView {
                    background: white;
                }
            """)
            self.setStyleSheet("""
                QWidget {
                    background: white;
                }
            """)
            layout.addWidget(self.site_preview)

            self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
            self.preview_size.currentIndexChanged.connect(self.adjust_preview_size)
            self.adjust_preview_size() # Set initial size

            # Install event filter for Escape key
            self.site_preview.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.site_preview and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape and self.fullscreen_window and self.fullscreen_window.isVisible():
                self.toggle_fullscreen()
                return True # Event handled
        return super().eventFilter(obj, event)

    def toggle_fullscreen(self):
        if HAS_WEBENGINE:
            if self.fullscreen_window is None:
                self.fullscreen_window = FullscreenPreviewWindow()
                self.fullscreen_window.exit_fullscreen_btn.clicked.connect(self.toggle_fullscreen)
                self.fullscreen_window.refresh_btn.clicked.connect(self.refresh_main_preview)
                self.fullscreen_window.preview_size.currentIndexChanged.connect(self.adjust_main_preview_size)

            if self.fullscreen_window.isVisible():
                self.fullscreen_window.site_preview.setParent(self)
                self.layout().addWidget(self.fullscreen_window.site_preview)
                self.fullscreen_window.hide()
                self.fullscreen_btn.setText('⛶ Fullscreen')
            else:
                self.site_preview.setParent(self.fullscreen_window.site_preview)
                self.fullscreen_window.layout.addWidget(self.site_preview)
                self.fullscreen_window.showFullScreen()
                self.fullscreen_btn.setText('🗗 Exit Fullscreen')
                self.fullscreen_window.load_url(self.site_preview.url())

    def adjust_preview_size(self):
        if HAS_WEBENGINE:
            mode = self.preview_size.currentText()
            if mode == 'Desktop':
                self.site_preview.setFixedSize(1024, 768) # Example desktop size
            elif mode == 'Tablet':
                self.site_preview.setFixedSize(768, 1024) # Example tablet size
            elif mode == 'Mobile':
                self.site_preview.setFixedSize(375, 667) # Example mobile size
            self.site_preview.update()

    def refresh_main_preview(self):
        # This method will be called from the fullscreen window's refresh button
        # It should trigger the update_preview in EditorView
        if self.parent() and hasattr(self.parent(), 'update_preview'):
            self.parent().update_preview()

    def adjust_main_preview_size(self):
        # This method will be called from the fullscreen window's size selector
        # It should update the size of the main preview
        if self.parent() and hasattr(self.parent(), 'update_preview'):
            self.adjust_preview_size()
