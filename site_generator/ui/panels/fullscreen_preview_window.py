from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMainWindow
from PyQt6.QtCore import Qt, QEvent, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

class FullscreenPreviewWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.site_preview = QWebEngineView()
        self.site_preview.setMinimumWidth(375)
        self.site_preview.setStyleSheet("""
            QWebEngineView {
                background: white;
            }
        """)

        self.create_controls()
        self.layout.addWidget(self.site_preview)

        self.site_preview.installEventFilter(self)

    def create_controls(self):
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(10)

        controls_layout.addWidget(QLabel('Preview:'))
        
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
        controls_layout.addWidget(self.preview_size)
        
        self.refresh_btn = QPushButton('↻ Atualizar')
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
        """)
        controls_layout.addWidget(self.refresh_btn)

        self.exit_fullscreen_btn = QPushButton('🗗 Exit Fullscreen')
        self.exit_fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
        """)
        controls_layout.addWidget(self.exit_fullscreen_btn)

        controls_layout.addStretch()
        self.layout.addLayout(controls_layout)

        self.preview_size.currentIndexChanged.connect(self.adjust_preview_size)
        self.adjust_preview_size() # Set initial size

    def load_url(self, url):
        self.site_preview.setUrl(url)

    def adjust_preview_size(self):
        mode = self.preview_size.currentText()
        if mode == 'Desktop':
            self.site_preview.setFixedSize(1024, 768) # Example desktop size
        elif mode == 'Tablet':
            self.site_preview.setFixedSize(768, 1024) # Example tablet size
        elif mode == 'Mobile':
            self.site_preview.setFixedSize(375, 667) # Example mobile size
        self.site_preview.update()

    def eventFilter(self, obj, event):
        if obj == self.site_preview and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True # Event handled
        return super().eventFilter(obj, event)
