
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QListWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
import os

class FileTreePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        tree_header = QLabel('Arquivos do Projeto')
        tree_header.setStyleSheet("""            QLabel {                color: #d4d4d4;                font-weight: bold;                padding: 5px;                background: #2d2d2d;                border-radius: 4px;            }        """)
        layout.addWidget(tree_header)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setStyleSheet("""            QTreeWidget {                background-color: #1e1e1e;                color: #d4d4d4;                border: none;            }            QTreeWidget::item {                padding: 4px;            }            QTreeWidget::item:selected {                background-color: #264f78;            }        """)
        self.file_tree.setMinimumWidth(200)
        self.file_tree.setMaximumWidth(400)
        layout.addWidget(self.file_tree)

        self.symbols_outline = QListWidget()
        self.symbols_outline.setMinimumHeight(80)
        self.symbols_outline.setMaximumHeight(200)
        self.symbols_outline.setStyleSheet("background: #23272e; color: #d4d4d4; border: none; font-size: 12px;")
        layout.addWidget(self.symbols_outline)

    def populate_file_tree(self, path):
        self.file_tree.clear()
        self.add_files(self.file_tree.invisibleRootItem(), path)

    def add_files(self, parent_item, path):
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            item = QTreeWidgetItem(parent_item, [file_name])
            item.setData(0, Qt.ItemDataRole.UserRole, file_path)
            if os.path.isdir(file_path):
                self.add_files(item, file_path)
