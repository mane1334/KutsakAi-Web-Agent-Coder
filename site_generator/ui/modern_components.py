"""
Componentes UI modernos para KutsakAI Web Agent Builder.
Design System baseado em Material Design 3 com elementos customizados.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QProgressBar, QScrollArea,
    QGraphicsDropShadowEffect, QGridLayout, QSizePolicy,
    QSpacerItem, QButtonGroup, QRadioButton, QCheckBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPainter, QColor, QBrush, QPen

class ModernCard(QFrame):
    """Card moderno com sombra e efeitos."""
    
    def __init__(self, title="", subtitle="", icon="", parent=None):
        super().__init__(parent)
        self.setup_ui(title, subtitle, icon)
        self.setup_effects()
    
    def setup_ui(self, title, subtitle, icon):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                border: 1px solid #2a2a2a;
                border-radius: 16px;
                padding: 20px;
                margin: 8px;
            }
            QFrame:hover {
                border-color: #10a37f;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #252525, stop: 1 #1f1f1f);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        if icon or title:
            header_layout = QHBoxLayout()
            
            if icon:
                icon_label = QLabel(icon)
                icon_label.setStyleSheet("""
                    QLabel {
                        font-size: 24px;
                        color: #10a37f;
                        background: transparent;
                        border: none;
                        padding: 0;
                        margin: 0;
                    }
                """)
                header_layout.addWidget(icon_label)
            
            if title:
                title_label = QLabel(title)
                title_label.setStyleSheet("""
                    QLabel {
                        color: #e6e6e6;
                        font-size: 18px;
                        font-weight: 600;
                        background: transparent;
                        border: none;
                        padding: 0;
                        margin: 0;
                    }
                """)
                header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            layout.addLayout(header_layout)
        
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font-size: 14px;
                    background: transparent;
                    border: none;
                    padding: 0;
                    margin: 0;
                }
            """)
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)
    
    def setup_effects(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class ModernButton(QPushButton):
    """Botão moderno com animações."""
    
    def __init__(self, text="", icon="", style="primary", parent=None):
        super().__init__(text, parent)
        self.button_style = style
        self.setup_style(icon)
        self.setup_animation()
    
    def setup_style(self, icon):
        if icon:
            self.setText(f"{icon} {self.text()}")
        
        if self.button_style == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #10a37f, stop: 1 #0d8a6c);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 120px;
                    box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #0d8a6c, stop: 1 #0a6b4f);
                    box-shadow: 0 6px 16px rgba(16, 163, 127, 0.4);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #0a6b4f, stop: 1 #085a42);
                    box-shadow: 0 2px 6px rgba(16, 163, 127, 0.2);
                }
                QPushButton:disabled {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #404040, stop: 1 #353535);
                    color: #808080;
                    box-shadow: none;
                }
            """)
        elif self.button_style == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #2a2a2a, stop: 1 #252525);
                    color: #e6e6e6;
                    border: 1px solid #3a3a3a;
                    padding: 12px 24px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 120px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #353535, stop: 1 #2f2f2f);
                    border-color: #4a4a4a;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
                }
            """)
        elif self.button_style == "danger":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #dc2626, stop: 1 #b91c1c);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                    min-width: 120px;
                    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #b91c1c, stop: 1 #991b1b);
                    box-shadow: 0 6px 16px rgba(220, 38, 38, 0.4);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #991b1b, stop: 1 #7f1d1d);
                    box-shadow: 0 2px 6px rgba(220, 38, 38, 0.2);
                }
            """)
    
    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

class ModernInput(QLineEdit):
    """Campo de entrada moderno."""
    
    def __init__(self, placeholder="", icon="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setup_style(icon)
    
    def setup_style(self, icon):
        if icon:
            self.setStyleSheet(f"""
                QLineEdit {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                    color: #e6e6e6;
                    border: 2px solid #3a3a3a;
                    border-radius: 10px;
                    padding: 12px 16px 12px 40px;
                    font-size: 14px;
                    selection-background-color: #10a37f;
                }}
                QLineEdit:focus {{
                    border: 2px solid #10a37f;
                    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.2);
                }}
                QLineEdit:before {{
                    content: '{icon}';
                    position: absolute;
                    left: 12px;
                    top: 50%;
                    transform: translateY(-50%);
                    color: #999999;
                    font-size: 16px;
                }}
            """)
        else:
            self.setStyleSheet("""
                QLineEdit {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                    color: #e6e6e6;
                    border: 2px solid #3a3a3a;
                    border-radius: 10px;
                    padding: 12px 16px;
                    font-size: 14px;
                    selection-background-color: #10a37f;
                }
                QLineEdit:focus {
                    border: 2px solid #10a37f;
                    box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.2);
                }
                QLineEdit::placeholder {
                    color: #666666;
                }
            """)

class ModernTextArea(QTextEdit):
    """Área de texto moderna."""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setup_style()
    
    def setup_style(self):
        self.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                color: #e6e6e6;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 16px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                selection-background-color: #10a37f;
            }
            QTextEdit:focus {
                border: 2px solid #10a37f;
                box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.2);
            }
        """)

class ModernProgressBar(QProgressBar):
    """Barra de progresso moderna."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
    
    def setup_style(self):
        self.setStyleSheet("""
            QProgressBar {
                background: #2a2a2a;
                border: none;
                border-radius: 8px;
                text-align: center;
                color: #e6e6e6;
                font-size: 12px;
                font-weight: 500;
                height: 16px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #10a37f, stop: 1 #0d8a6c);
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(16, 163, 127, 0.3);
            }
        """)

class LoadingSpinner(QLabel):
    """Spinner de carregamento animado."""
    
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        self.setFixedSize(self.size, self.size)
        self.setStyleSheet("background: transparent;")
    
    def setup_animation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # 50ms = ~20 FPS
    
    def rotate(self):
        self.angle = (self.angle + 15) % 360
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Configurar pen
        pen = QPen(QColor(16, 163, 127), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Desenhar círculo
        rect = QRect(3, 3, self.size - 6, self.size - 6)
        painter.drawArc(rect, self.angle * 16, 120 * 16)

class ToastNotification(QFrame):
    """Notificação toast moderna."""
    
    def __init__(self, message, type="info", duration=3000, parent=None):
        super().__init__(parent)
        self.duration = duration
        self.setup_ui(message, type)
        self.setup_animation()
        self.show_toast()
    
    def setup_ui(self, message, type):
        self.setFixedSize(350, 80)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Ícone
        icon_map = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        icon_label = QLabel(icon_map.get(type, "ℹ️"))
        icon_label.setStyleSheet("font-size: 20px; color: white;")
        
        # Mensagem
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
        """)
        message_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        
        # Estilo do container
        color_map = {
            "success": "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #10a37f, stop: 1 #0d8a6c);",
            "error": "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #dc2626, stop: 1 #b91c1c);",
            "warning": "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #f59e0b, stop: 1 #d97706);",
            "info": "background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #3b82f6, stop: 1 #2563eb);"
        }
        
        self.setStyleSheet(f"""
            QFrame {{
                {color_map.get(type, color_map["info"])}
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            }}
        """)
    
    def setup_animation(self):
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out.finished.connect(self.close)
    
    def show_toast(self):
        # Posicionar no canto superior direito
        screen = self.screen()
        if screen:
            screen_rect = screen.availableGeometry()
            self.move(screen_rect.width() - self.width() - 20, 20)
        
        self.show()
        self.fade_in.start()
        
        # Auto-fechar após duração
        QTimer.singleShot(self.duration, self.hide_toast)
    
    def hide_toast(self):
        self.fade_out.start()

class FeatureCard(ModernCard):
    """Card de funcionalidade com toggle."""
    
    feature_toggled = pyqtSignal(str, bool)
    
    def __init__(self, title, description, feature_key, enabled=True, parent=None):
        super().__init__(title, description, "⚡", parent)
        self.feature_key = feature_key
        self.enabled = enabled
        self.setup_toggle()
    
    def setup_toggle(self):
        toggle_layout = QHBoxLayout()
        
        self.toggle_checkbox = QCheckBox()
        self.toggle_checkbox.setChecked(self.enabled)
        self.toggle_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e6e6e6;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #3a3a3a;
                background: #1f1f1f;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #10a37f, stop: 1 #0d8a6c);
                border-color: #10a37f;
            }
        """)
        self.toggle_checkbox.toggled.connect(self.on_toggle)
        
        toggle_layout.addStretch()
        toggle_layout.addWidget(self.toggle_checkbox)
        
        self.layout().addLayout(toggle_layout)
    
    def on_toggle(self, checked):
        self.enabled = checked
        self.feature_toggled.emit(self.feature_key, checked)

def show_toast(parent, message, type="info", duration=3000):
    """Função utilitária para mostrar notificações toast."""
    toast = ToastNotification(message, type, duration, parent)
    return toast
