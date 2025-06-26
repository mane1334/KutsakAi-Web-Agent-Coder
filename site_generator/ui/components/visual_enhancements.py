"""
Visual Enhancements System
Provides modern UI components with animations, visual indicators,
and enhanced aesthetics for better user experience.
"""

import os
import math
from typing import Optional, List, Dict, Any
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QProgressBar, QScrollArea, QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
    QTabWidget, QListWidget, QListWidgetItem, QGroupBox, QApplication
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QSize,
    pyqtSignal, QParallelAnimationGroup, QSequentialAnimationGroup,
    QAbstractAnimation, QPoint, QObject, pyqtProperty
)
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QBrush, QPen, QFont, QFontMetrics,
    QPainterPath, QPixmap, QIcon, QPalette, QGradient
)

class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    LOADING = "loading"

class AnimationType(Enum):
    """Types of animations"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN_LEFT = "slide_in_left"
    SLIDE_IN_RIGHT = "slide_in_right"
    SLIDE_IN_UP = "slide_in_up"
    SLIDE_IN_DOWN = "slide_in_down"
    BOUNCE = "bounce"
    PULSE = "pulse"
    SHAKE = "shake"

class ModernButton(QPushButton):
    """Modern styled button with hover effects and animations"""
    
    def __init__(self, text: str = "", icon: str = "", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.hover_animation = None
        self.press_animation = None
        self.setup_style()
        self.setup_animations()
    
    def setup_style(self):
        """Setup modern button styling"""
        self.setStyleSheet("""
            ModernButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #4CAF50, stop: 1 #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                text-align: center;
                min-height: 20px;
            }
            ModernButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #45a049, stop: 1 #3d8b40);
                transform: translateY(-2px);
            }
            ModernButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #3d8b40, stop: 1 #2e7d32);
                transform: translateY(0px);
            }
            ModernButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def setup_animations(self):
        """Setup button animations"""
        # Hover animation
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Press animation
        self.press_animation = QPropertyAnimation(self, b"geometry")
        self.press_animation.setDuration(100)
        self.press_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        super().enterEvent(event)
        self.animate_hover(True)
    
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        super().leaveEvent(event)
        self.animate_hover(False)
    
    def animate_hover(self, hover: bool):
        """Animate hover effect"""
        if self.hover_animation.state() == QAbstractAnimation.State.Running:
            self.hover_animation.stop()
        
        current_rect = self.geometry()
        if hover:
            new_rect = QRect(current_rect.x(), current_rect.y() - 2, 
                           current_rect.width(), current_rect.height())
        else:
            new_rect = QRect(current_rect.x(), current_rect.y() + 2, 
                           current_rect.width(), current_rect.height())
        
        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(new_rect)
        self.hover_animation.start()

class StatusIndicator(QWidget):
    """Animated status indicator with different states"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = NotificationType.INFO
        self.animate_timer = QTimer()
        self.animate_timer.timeout.connect(self.update_animation)
        self.animation_frame = 0
        self.setFixedSize(20, 20)
    
    def set_status(self, status: NotificationType):
        """Set the status indicator type"""
        self.status = status
        if status == NotificationType.LOADING:
            self.animate_timer.start(50)  # 50ms interval for smooth animation
        else:
            self.animate_timer.stop()
        self.update()
    
    def update_animation(self):
        """Update animation frame"""
        self.animation_frame = (self.animation_frame + 1) % 360
        self.update()
    
    def paintEvent(self, event):
        """Paint the status indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 2 - 2
        
        if self.status == NotificationType.SUCCESS:
            # Green checkmark
            painter.setBrush(QBrush(QColor("#4CAF50")))
            painter.setPen(QPen(QColor("#4CAF50"), 2))
            painter.drawEllipse(center, radius, radius)
            
            # Draw checkmark
            painter.setPen(QPen(QColor("white"), 2))
            checkmark_path = QPainterPath()
            checkmark_path.moveTo(center.x() - 4, center.y())
            checkmark_path.lineTo(center.x() - 1, center.y() + 3)
            checkmark_path.lineTo(center.x() + 4, center.y() - 2)
            painter.drawPath(checkmark_path)
            
        elif self.status == NotificationType.ERROR:
            # Red X
            painter.setBrush(QBrush(QColor("#f44336")))
            painter.setPen(QPen(QColor("#f44336"), 2))
            painter.drawEllipse(center, radius, radius)
            
            # Draw X
            painter.setPen(QPen(QColor("white"), 2))
            painter.drawLine(center.x() - 3, center.y() - 3, center.x() + 3, center.y() + 3)
            painter.drawLine(center.x() - 3, center.y() + 3, center.x() + 3, center.y() - 3)
            
        elif self.status == NotificationType.WARNING:
            # Orange triangle with exclamation
            painter.setBrush(QBrush(QColor("#ff9800")))
            painter.setPen(QPen(QColor("#ff9800"), 2))
            painter.drawEllipse(center, radius, radius)
            
            # Draw exclamation
            painter.setPen(QPen(QColor("white"), 2))
            painter.drawLine(center.x(), center.y() - 4, center.x(), center.y() + 1)
            painter.drawPoint(center.x(), center.y() + 3)
            
        elif self.status == NotificationType.LOADING:
            # Spinning circle
            painter.setPen(QPen(QColor("#2196F3"), 3))
            painter.drawArc(center.x() - radius, center.y() - radius, 
                          radius * 2, radius * 2, 
                          self.animation_frame * 16, 90 * 16)
            
        else:  # INFO
            # Blue i
            painter.setBrush(QBrush(QColor("#2196F3")))
            painter.setPen(QPen(QColor("#2196F3"), 2))
            painter.drawEllipse(center, radius, radius)
            
            # Draw i
            painter.setPen(QPen(QColor("white"), 2))
            painter.drawPoint(center.x(), center.y() - 3)
            painter.drawLine(center.x(), center.y() - 1, center.x(), center.y() + 3)

class NotificationToast(QFrame):
    """Toast notification with auto-dismiss and animations"""
    
    dismissed = pyqtSignal()
    
    def __init__(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                 duration: int = 3000, parent=None):
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        
        self.setup_ui()
        self.setup_animations()
        
        # Auto dismiss timer
        if duration > 0:
            QTimer.singleShot(duration, self.dismiss)
    
    def setup_ui(self):
        """Setup the toast UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Status indicator
        self.status_indicator = StatusIndicator()
        self.status_indicator.set_status(self.notification_type)
        layout.addWidget(self.status_indicator)
        
        # Message
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 1)
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #666;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 10px;
            }
        """)
        self.close_btn.clicked.connect(self.dismiss)
        layout.addWidget(self.close_btn)
        
        # Style based on notification type
        self.apply_notification_style()
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
    
    def apply_notification_style(self):
        """Apply styling based on notification type"""
        styles = {
            NotificationType.SUCCESS: {
                'background': '#d4edda',
                'border': '#c3e6cb',
                'color': '#155724'
            },
            NotificationType.ERROR: {
                'background': '#f8d7da',
                'border': '#f5c6cb',
                'color': '#721c24'
            },
            NotificationType.WARNING: {
                'background': '#fff3cd',
                'border': '#ffeaa7',
                'color': '#856404'
            },
            NotificationType.INFO: {
                'background': '#d1ecf1',
                'border': '#bee5eb',
                'color': '#0c5460'
            },
            NotificationType.LOADING: {
                'background': '#e3f2fd',
                'border': '#bbdefb',
                'color': '#0d47a1'
            }
        }
        
        style = styles.get(self.notification_type, styles[NotificationType.INFO])
        
        self.setStyleSheet(f"""
            NotificationToast {{
                background-color: {style['background']};
                border: 1px solid {style['border']};
                border-radius: 8px;
                color: {style['color']};
            }}
        """)
    
    def setup_animations(self):
        """Setup enter/exit animations"""
        # Fade in animation
        self.fade_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.fade_effect)
        
        self.fade_in_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Slide in animation
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(300)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.OutBack)
        
    def show_animated(self, target_geometry: QRect):
        """Show with animation"""
        # Start from above the target position
        start_geometry = QRect(target_geometry.x(), target_geometry.y() - 50,
                             target_geometry.width(), target_geometry.height())
        
        self.setGeometry(start_geometry)
        self.show()
        
        # Animate slide down and fade in
        self.slide_animation.setStartValue(start_geometry)
        self.slide_animation.setEndValue(target_geometry)
        
        animation_group = QParallelAnimationGroup()
        animation_group.addAnimation(self.fade_in_animation)
        animation_group.addAnimation(self.slide_animation)
        animation_group.start()
    
    def dismiss(self):
        """Dismiss with animation"""
        # Fade out animation
        fade_out = QPropertyAnimation(self.fade_effect, b"opacity")
        fade_out.setDuration(200)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        fade_out.finished.connect(self.hide)
        fade_out.finished.connect(self.dismissed.emit)
        fade_out.start()

class ProgressIndicator(QWidget):
    """Modern progress indicator with multiple styles"""
    
    def __init__(self, style: str = "circular", parent=None):
        super().__init__(parent)
        self.style = style  # "circular", "linear", "dots"
        self.progress = 0
        self.animation_frame = 0
        self.animate_timer = QTimer()
        self.animate_timer.timeout.connect(self.update_animation)
        self.setFixedSize(50, 50)
    
    def set_progress(self, progress: int):
        """Set progress (0-100)"""
        self.progress = max(0, min(100, progress))
        self.update()
    
    def start_animation(self):
        """Start indeterminate animation"""
        self.animate_timer.start(50)
    
    def stop_animation(self):
        """Stop animation"""
        self.animate_timer.stop()
    
    def update_animation(self):
        """Update animation frame"""
        self.animation_frame = (self.animation_frame + 1) % 360
        self.update()
    
    def paintEvent(self, event):
        """Paint the progress indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.style == "circular":
            self.paint_circular(painter)
        elif self.style == "linear":
            self.paint_linear(painter)
        elif self.style == "dots":
            self.paint_dots(painter)
    
    def paint_circular(self, painter: QPainter):
        """Paint circular progress indicator"""
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = min(self.width(), self.height()) // 2 - 5
        
        # Background circle
        painter.setPen(QPen(QColor("#e0e0e0"), 3))
        painter.drawEllipse(center, radius, radius)
        
        # Progress arc
        if self.progress > 0:
            painter.setPen(QPen(QColor("#2196F3"), 3))
            start_angle = 90 * 16  # Start from top
            span_angle = -(self.progress * 360 // 100) * 16
            painter.drawArc(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2, start_angle, span_angle)
        
        # Indeterminate animation
        if self.animate_timer.isActive() and self.progress == 0:
            painter.setPen(QPen(QColor("#2196F3"), 3))
            start_angle = self.animation_frame * 16
            span_angle = 90 * 16
            painter.drawArc(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2, start_angle, span_angle)
    
    def paint_linear(self, painter: QPainter):
        """Paint linear progress indicator"""
        rect = QRect(5, self.height() // 2 - 2, self.width() - 10, 4)
        
        # Background
        painter.setBrush(QBrush(QColor("#e0e0e0")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 2, 2)
        
        # Progress
        if self.progress > 0:
            progress_width = rect.width() * self.progress // 100
            progress_rect = QRect(rect.x(), rect.y(), progress_width, rect.height())
            painter.setBrush(QBrush(QColor("#2196F3")))
            painter.drawRoundedRect(progress_rect, 2, 2)
        
        # Indeterminate animation
        if self.animate_timer.isActive() and self.progress == 0:
            bar_width = rect.width() // 4
            x_pos = (self.animation_frame * rect.width() // 360) % (rect.width() + bar_width) - bar_width
            progress_rect = QRect(rect.x() + x_pos, rect.y(), bar_width, rect.height())
            if progress_rect.right() > rect.x() and progress_rect.left() < rect.right():
                painter.setBrush(QBrush(QColor("#2196F3")))
                painter.drawRoundedRect(progress_rect, 2, 2)
    
    def paint_dots(self, painter: QPainter):
        """Paint dots progress indicator"""
        dot_count = 5
        dot_size = 6
        spacing = (self.width() - dot_count * dot_size) // (dot_count + 1)
        y = self.height() // 2
        
        for i in range(dot_count):
            x = spacing + i * (dot_size + spacing)
            
            if self.animate_timer.isActive():
                # Animated dots
                alpha = 50 + 205 * (math.sin((self.animation_frame + i * 60) * math.pi / 180) + 1) / 2
                color = QColor(33, 150, 243, int(alpha))
            else:
                # Static progress
                if i < (self.progress * dot_count // 100):
                    color = QColor("#2196F3")
                else:
                    color = QColor("#e0e0e0")
            
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x, y - dot_size // 2, dot_size, dot_size)

class AnimationManager:
    """Manages widget animations"""
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300, callback=None):
        """Fade in animation"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation
    
    @staticmethod
    def fade_out(widget: QWidget, duration: int = 300, callback=None):
        """Fade out animation"""
        effect = widget.graphicsEffect()
        if not effect:
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation
    
    @staticmethod
    def slide_in(widget: QWidget, direction: str = "left", duration: int = 300, callback=None):
        """Slide in animation"""
        original_geometry = widget.geometry()
        
        if direction == "left":
            start_geometry = QRect(-original_geometry.width(), original_geometry.y(),
                                 original_geometry.width(), original_geometry.height())
        elif direction == "right":
            start_geometry = QRect(widget.parent().width(), original_geometry.y(),
                                 original_geometry.width(), original_geometry.height())
        elif direction == "up":
            start_geometry = QRect(original_geometry.x(), -original_geometry.height(),
                                 original_geometry.width(), original_geometry.height())
        else:  # down
            start_geometry = QRect(original_geometry.x(), widget.parent().height(),
                                 original_geometry.width(), original_geometry.height())
        
        widget.setGeometry(start_geometry)
        widget.show()
        
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setStartValue(start_geometry)
        animation.setEndValue(original_geometry)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if callback:
            animation.finished.connect(callback)
        
        animation.start()
        return animation
    
    @staticmethod
    def bounce(widget: QWidget, duration: int = 600, callback=None):
        """Bounce animation"""
        original_geometry = widget.geometry()
        
        # Create bounce sequence
        animation_group = QSequentialAnimationGroup()
        
        # Up
        up_animation = QPropertyAnimation(widget, b"geometry")
        up_animation.setDuration(duration // 3)
        up_animation.setStartValue(original_geometry)
        up_rect = QRect(original_geometry.x(), original_geometry.y() - 10,
                       original_geometry.width(), original_geometry.height())
        up_animation.setEndValue(up_rect)
        up_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Down
        down_animation = QPropertyAnimation(widget, b"geometry")
        down_animation.setDuration(duration // 3)
        down_animation.setStartValue(up_rect)
        down_animation.setEndValue(original_geometry)
        down_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        
        # Small bounce
        small_up = QPropertyAnimation(widget, b"geometry")
        small_up.setDuration(duration // 6)
        small_up.setStartValue(original_geometry)
        small_up_rect = QRect(original_geometry.x(), original_geometry.y() - 3,
                             original_geometry.width(), original_geometry.height())
        small_up.setEndValue(small_up_rect)
        
        small_down = QPropertyAnimation(widget, b"geometry")
        small_down.setDuration(duration // 6)
        small_down.setStartValue(small_up_rect)
        small_down.setEndValue(original_geometry)
        
        animation_group.addAnimation(up_animation)
        animation_group.addAnimation(down_animation)
        animation_group.addAnimation(small_up)
        animation_group.addAnimation(small_down)
        
        if callback:
            animation_group.finished.connect(callback)
        
        animation_group.start()
        return animation_group
    
    @staticmethod
    def shake(widget: QWidget, duration: int = 400, callback=None):
        """Shake animation"""
        original_geometry = widget.geometry()
        
        animation_group = QSequentialAnimationGroup()
        shake_distance = 5
        shake_count = 4
        
        for i in range(shake_count):
            # Left
            left_animation = QPropertyAnimation(widget, b"geometry")
            left_animation.setDuration(duration // (shake_count * 2))
            left_rect = QRect(original_geometry.x() - shake_distance, original_geometry.y(),
                            original_geometry.width(), original_geometry.height())
            left_animation.setStartValue(original_geometry if i == 0 else right_rect)
            left_animation.setEndValue(left_rect)
            
            # Right
            right_animation = QPropertyAnimation(widget, b"geometry")
            right_animation.setDuration(duration // (shake_count * 2))
            right_rect = QRect(original_geometry.x() + shake_distance, original_geometry.y(),
                             original_geometry.width(), original_geometry.height())
            right_animation.setStartValue(left_rect)
            right_animation.setEndValue(right_rect)
            
            animation_group.addAnimation(left_animation)
            animation_group.addAnimation(right_animation)
        
        # Return to original position
        return_animation = QPropertyAnimation(widget, b"geometry")
        return_animation.setDuration(duration // (shake_count * 2))
        return_animation.setStartValue(right_rect)
        return_animation.setEndValue(original_geometry)
        animation_group.addAnimation(return_animation)
        
        if callback:
            animation_group.finished.connect(callback)
        
        animation_group.start()
        return animation_group

class NotificationManager(QObject):
    """Manages toast notifications"""
    
    def __init__(self, parent_widget: QWidget):
        super().__init__()
        self.parent_widget = parent_widget
        self.notifications = []
        self.notification_spacing = 10
        
    def show_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 3000):
        """Show a toast notification"""
        toast = NotificationToast(message, notification_type, duration, self.parent_widget)
        toast.dismissed.connect(lambda: self.remove_notification(toast))
        
        # Calculate position
        y_offset = 20
        for existing_toast in self.notifications:
            y_offset += existing_toast.height() + self.notification_spacing
        
        toast_width = 350
        toast_height = 60
        x_pos = self.parent_widget.width() - toast_width - 20
        
        target_geometry = QRect(x_pos, y_offset, toast_width, toast_height)
        
        self.notifications.append(toast)
        toast.show_animated(target_geometry)
        
        return toast
    
    def remove_notification(self, toast: NotificationToast):
        """Remove a notification and reposition others"""
        if toast in self.notifications:
            self.notifications.remove(toast)
            toast.deleteLater()
            
            # Reposition remaining notifications
            y_offset = 20
            for remaining_toast in self.notifications:
                current_geometry = remaining_toast.geometry()
                new_geometry = QRect(current_geometry.x(), y_offset,
                                   current_geometry.width(), current_geometry.height())
                
                # Animate to new position
                animation = QPropertyAnimation(remaining_toast, b"geometry")
                animation.setDuration(200)
                animation.setStartValue(current_geometry)
                animation.setEndValue(new_geometry)
                animation.setEasingCurve(QEasingCurve.Type.OutCubic)
                animation.start()
                
                y_offset += remaining_toast.height() + self.notification_spacing
    
    def show_success(self, message: str, duration: int = 3000):
        """Show success notification"""
        return self.show_notification(message, NotificationType.SUCCESS, duration)
    
    def show_error(self, message: str, duration: int = 5000):
        """Show error notification"""
        return self.show_notification(message, NotificationType.ERROR, duration)
    
    def show_warning(self, message: str, duration: int = 4000):
        """Show warning notification"""
        return self.show_notification(message, NotificationType.WARNING, duration)
    
    def show_info(self, message: str, duration: int = 3000):
        """Show info notification"""
        return self.show_notification(message, NotificationType.INFO, duration)
    
    def show_loading(self, message: str, duration: int = 0):
        """Show loading notification (doesn't auto-dismiss)"""
        return self.show_notification(message, NotificationType.LOADING, duration)

class ModernCard(QFrame):
    """Modern card component with shadow and hover effects"""
    
    def __init__(self, title: str = "", content: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.setup_ui()
        self.setup_effects()
    
    def setup_ui(self):
        """Setup card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("", 14, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #333; margin-bottom: 5px;")
            layout.addWidget(title_label)
        
        if self.content:
            content_label = QLabel(self.content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("color: #666; line-height: 1.4;")
            layout.addWidget(content_label)
        
        # Style the card
        self.setStyleSheet("""
            ModernCard {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
            }
            ModernCard:hover {
                border-color: #2196F3;
            }
        """)
    
    def setup_effects(self):
        """Setup visual effects"""
        # Drop shadow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)
        
        # Hover animation
        self.hover_animation = QPropertyAnimation(self.shadow, b"offset")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        super().enterEvent(event)
        self.hover_animation.setStartValue(self.shadow.offset())
        self.hover_animation.setEndValue(QPoint(0, 4))
        self.hover_animation.start()
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)
        self.hover_animation.setStartValue(self.shadow.offset())
        self.hover_animation.setEndValue(QPoint(0, 2))
        self.hover_animation.start()

class VisualEnhancementDemo(QWidget):
    """Demo widget showcasing all visual enhancements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notification_manager = NotificationManager(self)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup demo UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Visual Enhancements Demo")
        title.setFont(QFont("", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Buttons section
        buttons_group = QGroupBox("Modern Buttons")
        buttons_layout = QHBoxLayout(buttons_group)
        
        self.modern_btn = ModernButton("Modern Button", "🚀")
        buttons_layout.addWidget(self.modern_btn)
        
        success_btn = ModernButton("Success", "✅")
        success_btn.clicked.connect(lambda: self.notification_manager.show_success("Operation completed successfully!"))
        buttons_layout.addWidget(success_btn)
        
        error_btn = ModernButton("Error", "❌")
        error_btn.clicked.connect(lambda: self.notification_manager.show_error("Something went wrong!"))
        buttons_layout.addWidget(error_btn)
        
        layout.addWidget(buttons_group)
        
        # Progress indicators
        progress_group = QGroupBox("Progress Indicators")
        progress_layout = QHBoxLayout(progress_group)
        
        self.circular_progress = ProgressIndicator("circular")
        self.circular_progress.set_progress(75)
        progress_layout.addWidget(self.circular_progress)
        
        self.linear_progress = ProgressIndicator("linear")
        self.linear_progress.set_progress(50)
        progress_layout.addWidget(self.linear_progress)
        
        self.dots_progress = ProgressIndicator("dots")
        self.dots_progress.start_animation()
        progress_layout.addWidget(self.dots_progress)
        
        layout.addWidget(progress_group)
        
        # Cards section
        cards_group = QGroupBox("Modern Cards")
        cards_layout = QHBoxLayout(cards_group)
        
        card1 = ModernCard("Feature 1", "This is a modern card with hover effects and shadows.")
        cards_layout.addWidget(card1)
        
        card2 = ModernCard("Feature 2", "Cards provide a clean way to display information.")
        cards_layout.addWidget(card2)
        
        layout.addWidget(cards_group)
        
        # Animation controls
        animation_group = QGroupBox("Animations")
        animation_layout = QHBoxLayout(animation_group)
        
        fade_btn = ModernButton("Fade In")
        fade_btn.clicked.connect(lambda: AnimationManager.fade_in(card1))
        animation_layout.addWidget(fade_btn)
        
        bounce_btn = ModernButton("Bounce")
        bounce_btn.clicked.connect(lambda: AnimationManager.bounce(card2))
        animation_layout.addWidget(bounce_btn)
        
        shake_btn = ModernButton("Shake")
        shake_btn.clicked.connect(lambda: AnimationManager.shake(self.modern_btn))
        animation_layout.addWidget(shake_btn)
        
        layout.addWidget(animation_group)
        
        layout.addStretch()
