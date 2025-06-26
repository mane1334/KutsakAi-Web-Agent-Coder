"""
Advanced Command Palette System
Provides VS Code-like command palette with fuzzy search, quick actions,
and keyboard shortcuts.
"""

import os
import re
from typing import List, Dict, Callable, Optional, Any
from difflib import SequenceMatcher

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, 
    QListWidgetItem, QLabel, QPushButton, QWidget, QFrame,
    QApplication, QShortcut
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QPalette, QColor

class CommandAction:
    """Represents a command action in the palette"""
    
    def __init__(self, 
                 id: str,
                 title: str, 
                 description: str = "",
                 category: str = "General",
                 shortcut: str = "",
                 callback: Optional[Callable] = None,
                 icon: Optional[str] = None,
                 keywords: List[str] = None):
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.shortcut = shortcut
        self.callback = callback
        self.icon = icon
        self.keywords = keywords or []
        self.score = 0.0  # For fuzzy matching

class FuzzyMatcher:
    """Fuzzy string matching for command search"""
    
    @staticmethod
    def calculate_score(query: str, text: str) -> float:
        """Calculate fuzzy match score between query and text"""
        if not query:
            return 1.0
        
        query = query.lower()
        text = text.lower()
        
        # Exact match gets highest score
        if query in text:
            return 1.0 - (len(text) - len(query)) / len(text)
        
        # Character sequence matching
        matcher = SequenceMatcher(None, query, text)
        ratio = matcher.ratio()
        
        # Bonus for matching word boundaries
        words = text.split()
        word_match_bonus = 0
        for word in words:
            if word.startswith(query[:min(len(query), len(word))]):
                word_match_bonus += 0.3
        
        return min(1.0, ratio + word_match_bonus)
    
    @staticmethod
    def filter_and_sort(query: str, commands: List[CommandAction]) -> List[CommandAction]:
        """Filter and sort commands based on fuzzy matching"""
        if not query:
            return commands
        
        scored_commands = []
        for cmd in commands:
            # Calculate scores for different fields
            title_score = FuzzyMatcher.calculate_score(query, cmd.title)
            desc_score = FuzzyMatcher.calculate_score(query, cmd.description) * 0.7
            category_score = FuzzyMatcher.calculate_score(query, cmd.category) * 0.5
            
            # Check keywords
            keyword_score = 0
            for keyword in cmd.keywords:
                keyword_score = max(keyword_score, FuzzyMatcher.calculate_score(query, keyword))
            keyword_score *= 0.8
            
            # Combined score
            cmd.score = max(title_score, desc_score, category_score, keyword_score)
            
            # Only include commands with reasonable scores
            if cmd.score > 0.3:
                scored_commands.append(cmd)
        
        # Sort by score (descending)
        scored_commands.sort(key=lambda x: x.score, reverse=True)
        return scored_commands

class CommandPaletteItem(QWidget):
    """Custom widget for command palette items"""
    
    def __init__(self, command: CommandAction):
        super().__init__()
        self.command = command
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Icon (if available)
        if self.command.icon:
            icon_label = QLabel()
            icon_label.setText(self.command.icon)  # Use emoji or text icon
            icon_label.setFixedSize(24, 24)
            layout.addWidget(icon_label)
        
        # Main content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        # Title
        title_label = QLabel(self.command.title)
        title_label.setFont(QFont("", 10, QFont.Weight.Bold))
        content_layout.addWidget(title_label)
        
        # Description
        if self.command.description:
            desc_label = QLabel(self.command.description)
            desc_label.setStyleSheet("color: #666; font-size: 9px;")
            content_layout.addWidget(desc_label)
        
        layout.addLayout(content_layout, 1)
        
        # Shortcut
        if self.command.shortcut:
            shortcut_label = QLabel(self.command.shortcut)
            shortcut_label.setStyleSheet("""
                background: #e0e0e0; 
                border-radius: 3px; 
                padding: 2px 6px; 
                font-size: 8px;
                color: #333;
            """)
            shortcut_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(shortcut_label)
        
        # Category
        category_label = QLabel(self.command.category)
        category_label.setStyleSheet("""
            background: #4CAF50; 
            color: white; 
            border-radius: 8px; 
            padding: 2px 8px; 
            font-size: 8px;
        """)
        category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(category_label)

class CommandPalette(QDialog):
    """Main command palette dialog"""
    
    command_executed = pyqtSignal(str)  # Emits command ID when executed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.commands: List[CommandAction] = []
        self.filtered_commands: List[CommandAction] = []
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.setup_ui()
        self.setup_default_commands()
        self.setup_shortcuts()
    
    def setup_ui(self):
        self.setWindowTitle("Command Palette")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set size and position
        self.setFixedSize(600, 400)
        self.center_on_screen()
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container with rounded corners
        self.container = QFrame()
        self.container.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #ccc;
            }
        """)
        layout.addWidget(self.container)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #45a049;
            }
        """)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.execute_selected_command)
        container_layout.addWidget(self.search_input)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                border: none;
                outline: none;
                background: transparent;
            }
            QListWidget::item {
                border: none;
                padding: 5px;
                border-radius: 5px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                border: 1px solid #2196F3;
            }
            QListWidget::item:hover {
                background: #f5f5f5;
            }
        """)
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        container_layout.addWidget(self.results_list)
        
        # Footer with help text
        footer = QLabel("↑↓ Navigate • Enter Execute • Esc Close")
        footer.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(footer)
        
        # Initially populate with all commands
        self.populate_results(self.commands)
    
    def center_on_screen(self):
        """Center the dialog on the screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2 - 100  # Slightly above center
        )
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Escape to close
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)
        
        # Up/Down navigation
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, self.select_previous)
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, self.select_next)
        
        # Ctrl+P to open (will be connected by parent)
        self.toggle_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), self.parent())
        if self.parent():
            self.toggle_shortcut.activated.connect(self.toggle_visibility)
    
    def setup_default_commands(self):
        """Setup default commands"""
        self.commands = [
            # File Operations
            CommandAction("file.new", "New File", "Create a new file", "File", "Ctrl+N", 
                         icon="📄", keywords=["create", "add"]),
            CommandAction("file.open", "Open File", "Open an existing file", "File", "Ctrl+O", 
                         icon="📂", keywords=["load"]),
            CommandAction("file.save", "Save File", "Save the current file", "File", "Ctrl+S", 
                         icon="💾", keywords=["store"]),
            CommandAction("file.save_all", "Save All", "Save all open files", "File", "Ctrl+Shift+S", 
                         icon="💾", keywords=["store", "all"]),
            
            # Project Operations
            CommandAction("project.open", "Open Project", "Open a project folder", "Project", "", 
                         icon="📁", keywords=["folder", "workspace"]),
            CommandAction("project.close", "Close Project", "Close current project", "Project", "", 
                         icon="✖️", keywords=["shutdown"]),
            
            # View Operations
            CommandAction("view.toggle_preview", "Toggle Preview", "Show/hide live preview", "View", "F5", 
                         icon="👁️", keywords=["show", "hide", "preview"]),
            CommandAction("view.toggle_devtools", "Toggle Developer Tools", "Show/hide dev tools", "View", "F12", 
                         icon="🔧", keywords=["debug", "console"]),
            CommandAction("view.fullscreen", "Toggle Fullscreen", "Enter/exit fullscreen mode", "View", "F11", 
                         icon="⛶", keywords=["maximize"]),
            
            # Editor Operations
            CommandAction("editor.format", "Format Document", "Format the current document", "Editor", "Shift+Alt+F", 
                         icon="🎨", keywords=["beautify", "indent"]),
            CommandAction("editor.find", "Find", "Search in current file", "Editor", "Ctrl+F", 
                         icon="🔍", keywords=["search"]),
            CommandAction("editor.replace", "Find and Replace", "Find and replace text", "Editor", "Ctrl+H", 
                         icon="🔄", keywords=["substitute"]),
            CommandAction("editor.goto_line", "Go to Line", "Jump to specific line number", "Editor", "Ctrl+G", 
                         icon="➡️", keywords=["jump", "navigate"]),
            
            # AI Operations
            CommandAction("ai.improve_code", "AI: Improve Code", "Use AI to improve current code", "AI", "", 
                         icon="🤖", keywords=["artificial", "enhance", "optimize"]),
            CommandAction("ai.generate_code", "AI: Generate Code", "Generate code from description", "AI", "", 
                         icon="✨", keywords=["create", "artificial"]),
            CommandAction("ai.explain_code", "AI: Explain Code", "Get AI explanation of selected code", "AI", "", 
                         icon="💬", keywords=["describe", "artificial"]),
            
            # Git Operations
            CommandAction("git.status", "Git: Status", "Show git status", "Git", "", 
                         icon="📊", keywords=["version", "control"]),
            CommandAction("git.commit", "Git: Commit", "Commit changes", "Git", "", 
                         icon="✅", keywords=["save", "version"]),
            CommandAction("git.push", "Git: Push", "Push to remote repository", "Git", "", 
                         icon="⬆️", keywords=["upload", "remote"]),
            CommandAction("git.pull", "Git: Pull", "Pull from remote repository", "Git", "", 
                         icon="⬇️", keywords=["download", "sync"]),
            
            # Settings
            CommandAction("settings.preferences", "Preferences", "Open preferences", "Settings", "Ctrl+,", 
                         icon="⚙️", keywords=["config", "options"]),
            CommandAction("settings.shortcuts", "Keyboard Shortcuts", "View/edit shortcuts", "Settings", "", 
                         icon="⌨️", keywords=["hotkeys", "bindings"]),
            
            # Help
            CommandAction("help.about", "About", "About this application", "Help", "", 
                         icon="ℹ️", keywords=["info", "version"]),
            CommandAction("help.docs", "Documentation", "Open documentation", "Help", "F1", 
                         icon="📚", keywords=["manual", "guide"]),
        ]
    
    def add_command(self, command: CommandAction):
        """Add a new command to the palette"""
        self.commands.append(command)
    
    def remove_command(self, command_id: str):
        """Remove a command by ID"""
        self.commands = [cmd for cmd in self.commands if cmd.id != command_id]
    
    def on_search_text_changed(self, text: str):
        """Handle search text changes with debouncing"""
        self.search_timer.stop()
        self.search_timer.start(150)  # 150ms delay
    
    def perform_search(self):
        """Perform the actual search"""
        query = self.search_input.text().strip()
        
        if query:
            self.filtered_commands = FuzzyMatcher.filter_and_sort(query, self.commands)
        else:
            self.filtered_commands = self.commands[:]
        
        self.populate_results(self.filtered_commands)
    
    def populate_results(self, commands: List[CommandAction]):
        """Populate the results list with commands"""
        self.results_list.clear()
        
        for command in commands[:20]:  # Limit to top 20 results
            item = QListWidgetItem()
            item_widget = CommandPaletteItem(command)
            item.setSizeHint(item_widget.sizeHint())
            
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, item_widget)
            
            # Store command reference
            item.setData(Qt.ItemDataRole.UserRole, command)
        
        # Select first item if available
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
    
    def select_previous(self):
        """Select previous item in the list"""
        current_row = self.results_list.currentRow()
        if current_row > 0:
            self.results_list.setCurrentRow(current_row - 1)
    
    def select_next(self):
        """Select next item in the list"""
        current_row = self.results_list.currentRow()
        if current_row < self.results_list.count() - 1:
            self.results_list.setCurrentRow(current_row + 1)
    
    def execute_selected_command(self):
        """Execute the currently selected command"""
        current_item = self.results_list.currentItem()
        if current_item:
            command = current_item.data(Qt.ItemDataRole.UserRole)
            self.execute_command(command)
    
    def on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click"""
        command = item.data(Qt.ItemDataRole.UserRole)
        self.execute_command(command)
    
    def execute_command(self, command: CommandAction):
        """Execute a command"""
        if command.callback:
            try:
                command.callback()
            except Exception as e:
                print(f"Error executing command {command.id}: {e}")
        
        # Emit signal
        self.command_executed.emit(command.id)
        
        # Close palette
        self.close()
    
    def toggle_visibility(self):
        """Toggle the visibility of the command palette"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            self.search_input.setFocus()
            self.search_input.clear()
            self.perform_search()  # Reset to show all commands
    
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            # Let the shortcuts handle navigation
            pass
        else:
            # Focus search input for typing
            if not self.search_input.hasFocus():
                self.search_input.setFocus()
            super().keyPressEvent(event)

class CommandManager:
    """Manages command registration and execution"""
    
    def __init__(self):
        self.palette = None
        self.command_handlers: Dict[str, Callable] = {}
    
    def create_palette(self, parent=None) -> CommandPalette:
        """Create a new command palette instance"""
        self.palette = CommandPalette(parent)
        self.palette.command_executed.connect(self.handle_command)
        return self.palette
    
    def register_command(self, command: CommandAction, handler: Callable = None):
        """Register a command with optional handler"""
        if self.palette:
            self.palette.add_command(command)
        
        if handler:
            self.command_handlers[command.id] = handler
            command.callback = handler
    
    def handle_command(self, command_id: str):
        """Handle command execution"""
        if command_id in self.command_handlers:
            try:
                self.command_handlers[command_id]()
            except Exception as e:
                print(f"Error executing command {command_id}: {e}")
    
    def show_palette(self):
        """Show the command palette"""
        if self.palette:
            self.palette.toggle_visibility()
