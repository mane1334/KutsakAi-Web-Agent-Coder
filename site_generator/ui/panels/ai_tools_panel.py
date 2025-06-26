from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
    QProgressBar, QCheckBox, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont
from ollama_client import list_models
import datetime

class AIToolsPanel(QWidget):
    # Signals for new functionality
    request_improve = pyqtSignal(str, str)  # prompt, model
    restore_history = pyqtSignal(str)  # history_entry_id
    save_as_snippet = pyqtSignal(str)  # text_content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_prompt = ""  # Store last prompt for smart snippet naming
        self.setup_ui()

    def create_streaming_section(self, layout):
        """Create the UI section to show streaming status like progress bar and text"""
        streaming_layout = QVBoxLayout()
        streaming_layout.setContentsMargins(0, 0, 0, 0)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)  # Hidden by default
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                background: #2a2a2a;
                height: 6px;
            }
            QProgressBar::chunk {
                background: #10a37f;
                border-radius: 3px;
            }
        """)
        streaming_layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel('Ready')
        self.status_label.setStyleSheet("color: #e6e6e6; font-size: 11px; padding: 4px;")
        streaming_layout.addWidget(self.status_label)

        streaming_section = QFrame()
        streaming_section.setLayout(streaming_layout)
        streaming_section.setStyleSheet("background: #1a1a1a; border-radius: 4px; padding: 8px; margin: 4px 0;")
        layout.addWidget(streaming_section)

    def create_history_section(self, layout):
        """Create the UI section to display history of improvements"""
        history_layout = QVBoxLayout()

        history_label = QLabel('History')
        history_label.setStyleSheet("color: #e6e6e6; font-weight: 500; margin-top: 8px;")
        history_layout.addWidget(history_label)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background: #1a1a1a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 4px;
                font-size: 11px;
                max-height: 120px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #2a2a2a;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: #10a37f;
                color: white;
            }
            QListWidget::item:hover {
                background: #2a2a2a;
            }
        """)
        self.history_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        history_layout.addWidget(self.history_list)

        layout.addLayout(history_layout)

    def connect_signals(self):
        """Connect signals to slots"""
        self.improve_btn.clicked.connect(self.on_improve_clicked)
        self.history_list.itemDoubleClicked.connect(self.on_history_item_double_clicked)
        self.save_snippet_btn.clicked.connect(self.on_save_snippet_clicked)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header = QLabel('🤖 AI Tools')
        header.setFont(QFont('Segoe UI', 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #e6e6e6; margin-bottom: 8px;")
        layout.addWidget(header)

        # Model Selection
        model_layout = QHBoxLayout()
        model_label = QLabel('Model:')
        model_label.setStyleSheet("color: #e6e6e6; font-weight: 500;")
        model_layout.addWidget(model_label)
        self.model_combo = QComboBox()
        self.model_combo.addItems(list_models())
        self.model_combo.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                padding: 6px;
                border-radius: 4px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e6e6e6;
            }
        """)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        layout.addLayout(model_layout)

        # Improvement Prompt
        prompt_label = QLabel('Improvement Prompt:')
        prompt_label.setStyleSheet("color: #e6e6e6; font-weight: 500; margin-top: 8px;")
        layout.addWidget(prompt_label)
        self.improve_input = QLineEdit()
        self.improve_input.setPlaceholderText('Describe the desired improvements...')
        self.improve_input.setStyleSheet("""
            QLineEdit {
                background: #2a2a2a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                padding: 8px;
                border-radius: 4px;
                font-size: 11px;
            }
            QLineEdit:focus {
                border-color: #10a37f;
            }
        """)
        layout.addWidget(self.improve_input)

        # Streaming Status Section
        self.create_streaming_section(layout)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.improve_btn = QPushButton('✨ Improve with AI')
        self.improve_all_btn = QPushButton('✨ Improve All Files')
        self.loop_ia_btn = QPushButton('🔁 Loop IA (5x)')

        for btn in [self.improve_btn, self.improve_all_btn, self.loop_ia_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #10a37f;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background: #0d8f73;
                }
                QPushButton:pressed {
                    background: #0a7862;
                }
                QPushButton:disabled {
                    background: #3a3a3a;
                    color: #888;
                }
            """)

        button_layout.addWidget(self.improve_btn)
        button_layout.addWidget(self.improve_all_btn)
        button_layout.addWidget(self.loop_ia_btn)
        layout.addLayout(button_layout)

        # Auto-save checkbox
        self.auto_save_checkbox = QCheckBox('Auto-save on finish')
        self.auto_save_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e6e6e6;
                font-size: 11px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background: #10a37f;
                border-color: #10a37f;
            }
        """)
        self.auto_save_checkbox.setChecked(True)
        layout.addWidget(self.auto_save_checkbox)
        
        # Add to Snippets checkbox
        self.add_to_snippets_checkbox = QCheckBox('📋 Add to Snippets after improvement')
        self.add_to_snippets_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e6e6e6;
                font-size: 11px;
                spacing: 8px;
                margin-top: 4px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background: #6366f1;
                border-color: #6366f1;
            }
        """)
        self.add_to_snippets_checkbox.setChecked(False)  # Optional by default
        layout.addWidget(self.add_to_snippets_checkbox)

        # History Section
        self.create_history_section(layout)

        # Save as Snippet Button
        self.save_snippet_btn = QPushButton('📋 Save as Snippet')
        self.save_snippet_btn.setStyleSheet("""
            QPushButton {
                background: #2a2a2a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
                margin-top: 8px;
            }
            QPushButton:hover {
                background: #353535;
                border-color: #4a4a4a;
            }
            QPushButton:pressed {
                background: #404040;
            }
        """)
        layout.addWidget(self.save_snippet_btn)

        # Connect signals
        self.connect_signals()

        layout.addStretch()  # Push content to the top

    # Slots
    def on_improve_clicked(self):
        prompt = self.improve_input.text()
        prompt = prompt.strip()
        model = self.model_combo.currentText()
        self.last_prompt = prompt  # Store for smart snippet naming
        self.request_improve.emit(prompt, model)

    def on_history_item_double_clicked(self, item):
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        self.restore_history.emit(entry_id)

    def on_save_snippet_clicked(self):
        # This will be handled by the parent to get selected text or whole file content
        self.save_as_snippet.emit("")

    # Public methods for external control
    def show_streaming(self, status_text="Improving..."):
        """Show progress bar and update status"""
        self.progress_bar.setVisible(True)
        self.status_label.setText(status_text)
        self.set_buttons_enabled(False)

    def hide_streaming(self):
        """Hide progress bar and reset status"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        self.set_buttons_enabled(True)

    def set_buttons_enabled(self, enabled):
        """Enable or disable action buttons"""
        self.improve_btn.setEnabled(enabled)
        self.improve_all_btn.setEnabled(enabled)
        self.loop_ia_btn.setEnabled(enabled)

    def add_history_entry(self, timestamp, prompt, model):
        """Add a new entry to the history list"""
        entry_text = f"{timestamp.strftime('%H:%M:%S')} - {prompt[:30]}... ({model})"
        item = QListWidgetItem(entry_text)
        item.setData(Qt.ItemDataRole.UserRole, f"{timestamp.isoformat()}")
        self.history_list.insertItem(0, item)
        
        # Keep only last 10 entries
        while self.history_list.count() > 10:
            self.history_list.takeItem(self.history_list.count() - 1)

    def clear_history(self):
        """Clear all history entries"""
        self.history_list.clear()

    def is_auto_save_enabled(self):
        """Check if auto-save is enabled"""
        return self.auto_save_checkbox.isChecked()
    
    def is_add_to_snippets_enabled(self):
        """Check if add to snippets after improvement is enabled"""
        return self.add_to_snippets_checkbox.isChecked()
