import difflib
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPlainTextEdit, QLabel, QPushButton, QFrame
)
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor, QFont
from PyQt6.QtCore import Qt

class DiffView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Barra de ferramentas do Diff
        toolbar = QHBoxLayout()
        self.title = QLabel("🔍 Revisão de Alterações")
        self.title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.title.setStyleSheet("color: #e6e6e6;")
        toolbar.addWidget(self.title)
        toolbar.addStretch()
        
        self.accept_btn = QPushButton("✅ Aceitar Alterações")
        self.accept_btn.setStyleSheet("""
            QPushButton {
                background: #10a37f;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover { background: #0d8a6c; }
        """)
        
        self.reject_btn = QPushButton("❌ Rejeitar")
        self.reject_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover { background: #dc2626; }
        """)
        
        toolbar.addWidget(self.reject_btn)
        toolbar.addWidget(self.accept_btn)
        layout.addLayout(toolbar)

        # Visualização lado a lado
        editors_layout = QHBoxLayout()
        
        # Original
        original_container = QVBoxLayout()
        original_container.addWidget(QLabel("Original"))
        self.original_editor = QPlainTextEdit()
        self.original_editor.setReadOnly(True)
        self.original_editor.setStyleSheet("background: #1a1a1a; color: #888; border: 1px solid #2a2a2a;")
        original_container.addWidget(self.original_editor)
        editors_layout.addLayout(original_container)
        
        # Proposta
        proposed_container = QVBoxLayout()
        proposed_container.addWidget(QLabel("Proposta (IA)"))
        self.proposed_editor = QPlainTextEdit()
        self.proposed_editor.setReadOnly(True)
        self.proposed_editor.setStyleSheet("background: #1a1a1a; color: #fff; border: 1px solid #2a2a2a;")
        proposed_container.addWidget(self.proposed_editor)
        editors_layout.addLayout(proposed_container)
        
        layout.addLayout(editors_layout)

    def set_diff(self, old_code, new_code):
        """Calcula e exibe o diff entre o código antigo e o novo."""
        self.original_editor.setPlainText(old_code)
        self.proposed_editor.setPlainText(new_code)
        
        # Formatação básica de cores para o diff
        self.highlight_diff(old_code, new_code)

    def highlight_diff(self, old_code, new_code):
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()
        
        d = difflib.Differ()
        diff = list(d.compare(old_lines, new_lines))
        
        # Limpar formatação anterior
        self.proposed_editor.clear()
        
        cursor = self.proposed_editor.textCursor()
        
        for line in diff:
            format = QTextCharFormat()
            if line.startswith('+ '):
                format.setBackground(QColor(16, 163, 127, 40)) # Verde transparente
                cursor.insertText(line[2:] + '\n', format)
            elif line.startswith('- '):
                # No editor proposto, não mostramos o que foi removido, 
                # apenas o resultado final com destaque nas adições
                pass
            elif line.startswith('  '):
                cursor.insertText(line[2:] + '\n')
            elif line.startswith('? '):
                pass
