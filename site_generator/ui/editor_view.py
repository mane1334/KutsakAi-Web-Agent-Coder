import os
import json
import datetime
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSplitter, QTabWidget,
    QLineEdit, QTreeWidget, QListWidget, QFrame,
    QMessageBox, QFileDialog, QTreeWidgetItem, QToolBar,
    QStatusBar, QProgressBar, QTextEdit, QGroupBox,
    QCheckBox, QSlider, QSpinBox, QInputDialog, QDialog
)
from PyQt6.QtCore import Qt, QEvent, QUrl, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QFont, QAction, QPixmap, QSyntaxHighlighter, QTextCharFormat, QColor
import os

from .panels.file_tree_panel import FileTreePanel
from .panels.preview_panel import PreviewPanel
from .panels.git_panel import GitPanel
from ..logic.editor_controller import EditorController
from site_generator.project_manager import ProjectManager

from .custom_editor_widget import VSCTextEdit

from .panels.ai_tools_panel import AIToolsPanel

class EditorView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = EditorController(self)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle('KutsakAI Web Agent Builder')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'assets', 'kutsakai_icon.png')))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        self.create_toolbar()
        main_layout.addWidget(self.toolbar)

        # Main Content
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_layout.addWidget(main_splitter)

        # Left Panel (File Tree)
        self.file_tree_panel = FileTreePanel()
        main_splitter.addWidget(self.file_tree_panel)

        # Center Section: Vertical Splitter for Editor and Bottom Panels
        center_vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        center_vertical_splitter.setChildrenCollapsible(False)
        main_splitter.addWidget(center_vertical_splitter)

        # Editor Tabs (Top part of center section)
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_editor_tab)
        editor_layout.addWidget(self.editor_tabs)
        center_vertical_splitter.addWidget(editor_container)

        # Bottom Panel (Bottom part of center section)
        self.create_bottom_panel()
        center_vertical_splitter.addWidget(self.bottom_panel)

        # Right Panel (Preview)
        self.preview_panel = PreviewPanel()
        main_splitter.addWidget(self.preview_panel)

        main_splitter.setSizes([200, 600, 400])
        center_vertical_splitter.setSizes([700, 300])

        self.connect_signals()
        
        # Initialize streaming state
        self.pending_improvements = 0
        self.loop_iteration = 0
        self.loop_total = 0
        self.loop_prompt = ""
        self.loop_model = ""
        self.loop_file_path = ""
        
        # Status bar for messages
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background: #2a2a2a; color: #e6e6e6; border-top: 1px solid #3a3a3a;")
        main_layout.addWidget(self.status_bar)
        self.set_status_message("Ready")

    def create_toolbar(self):
        self.toolbar = QFrame()
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_layout.setSpacing(10)

        # Project Controls
        self.open_project_btn = QPushButton('Open Project')
        self.save_all_btn = QPushButton('Save All')
        toolbar_layout.addWidget(self.open_project_btn)
        toolbar_layout.addWidget(self.save_all_btn)

        self.project_path_label = QLabel('No project open')
        toolbar_layout.addWidget(self.project_path_label, 1)

    def create_bottom_panel(self):
        self.bottom_panel = QTabWidget()
        self.bottom_panel.setTabPosition(QTabWidget.TabPosition.South)

        # Git Panel
        self.git_panel = GitPanel()
        self.bottom_panel.addTab(self.git_panel, 'Git')

# Problems Panel
        self.problems_panel = QListWidget()
        self.problems_panel.setStyleSheet("background: #1a1a1a; color: #e6e6e6; font-size: 11px;")
        self.problems_panel.setMinimumHeight(100)
        self.bottom_panel.addTab(self.problems_panel, 'Problems')
        # Fake problem data for demonstration
        self.problems_panel.addItem('Line 10: Variable is not used')
        self.problems_panel.addItem('Line 22: Function is missing a return statement')
        self.problems_panel.addItem('Line 45: Possible undefined variable')

        # Snippets Panel
        self.create_snippets_panel()
        self.bottom_panel.addTab(self.snippets_widget, 'Snippets')

# AI Tools Panel
        self.ai_tools_panel = AIToolsPanel()
        self.bottom_panel.addTab(self.ai_tools_panel, 'AI Tools')
        
        # Example hook-up
        self.ai_tools_panel.improve_btn.clicked.connect(self.analyze_code)

    def create_snippets_panel(self):
        self.snippets_widget = QWidget()
        snippets_layout = QVBoxLayout(self.snippets_widget)
        snippets_layout.setContentsMargins(8, 8, 8, 8)
        snippets_layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('📝 Code Snippets')
        title.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6e6e6; margin-bottom: 4px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        snippets_layout.addLayout(header_layout)
        
        # Snippets list
        self.snippets_panel = QListWidget()
        self.snippets_panel.setStyleSheet("""
            QListWidget {
                background: #1a1a1a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 4px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
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
        snippets_layout.addWidget(self.snippets_panel)
        
        # Action buttons
        snippet_btns_layout = QHBoxLayout()
        
        self.add_snippet_btn = QPushButton('➕ Add')
        self.remove_snippet_btn = QPushButton('🗑️ Remove')
        self.insert_snippet_btn = QPushButton('📋 Insert')
        
        for btn in [self.add_snippet_btn, self.remove_snippet_btn, self.insert_snippet_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #2a2a2a;
                    color: #e6e6e6;
                    border: 1px solid #3a3a3a;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #353535;
                    border-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background: #404040;
                }
            """)
        
        snippet_btns_layout.addWidget(self.add_snippet_btn)
        snippet_btns_layout.addWidget(self.remove_snippet_btn)
        snippet_btns_layout.addWidget(self.insert_snippet_btn)
        snippets_layout.addLayout(snippet_btns_layout)
        
        # Load snippets
        self.load_snippets()

    def connect_signals(self):
        self.open_project_btn.clicked.connect(self.on_open_project)
        self.save_all_btn.clicked.connect(self.on_save_all)
        self.file_tree_panel.file_tree.itemDoubleClicked.connect(self.on_file_tree_double_click)
        self.add_snippet_btn.clicked.connect(self.on_add_snippet)
        self.remove_snippet_btn.clicked.connect(self.on_remove_snippet)
        self.insert_snippet_btn.clicked.connect(self.on_insert_snippet)
        self.snippets_panel.itemDoubleClicked.connect(self.on_insert_snippet)
        self.editor_tabs.currentChanged.connect(self.update_preview)
        self.preview_panel.refresh_btn.clicked.connect(self.update_preview)

        # AI Tools Panel Signals
        self.ai_tools_panel.improve_btn.clicked.connect(self.on_improve)
        self.ai_tools_panel.improve_all_btn.clicked.connect(self.on_improve_all)
        self.ai_tools_panel.loop_ia_btn.clicked.connect(self.on_loop_ia)
        
        # New AI Tools Panel Signals
        self.ai_tools_panel.request_improve.connect(self.on_request_improve)
        self.ai_tools_panel.restore_history.connect(self.on_restore_history)
        self.ai_tools_panel.save_as_snippet.connect(self.on_save_as_snippet)
        
        # Connect controller signals for streaming
        self.controller.token_received.connect(self.on_token_received)
        self.controller.improvement_finished.connect(self.on_improvement_finished)
        self.controller.improvement_error.connect(self.on_improvement_error)
        self.controller.improvement_started.connect(self.on_improvement_started)

    def on_open_project(self):
        path = QFileDialog.getExistingDirectory(self, 'Open Project')
        if path:
            self.project_path_label.setText(path)
            self.file_tree_panel.populate_file_tree(path)
            self.controller.load_project(path)
            
            # Set project path for Git panel
            self.git_panel.set_project_path(path)
            
            self.update_preview()

    def on_save_all(self):
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            file_path = editor.property('file_path')
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
        QMessageBox.information(self, 'Success', 'All files saved successfully.')
        self.update_preview()

    def update_preview(self):
        current_tab = self.editor_tabs.currentWidget()
        if current_tab and hasattr(current_tab, 'property'):
            file_path = current_tab.property('file_path')
            if file_path and file_path.endswith('.html'):
                self.preview_panel.site_preview.setUrl(QUrl.fromLocalFile(file_path))
            elif self.project_path_label.text() != 'No project open':
                project_path = self.project_path_label.text()
                html_path = os.path.join(project_path, 'index.html')
                if os.path.exists(html_path):
                    self.preview_panel.site_preview.setUrl(QUrl.fromLocalFile(html_path))

    def on_improve(self):
        """Start async improvement for current file"""
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return

        prompt = self.ai_tools_panel.improve_input.text()
        prompt = prompt.strip()
        model = self.ai_tools_panel.model_combo.currentText()
        file_path = editor.property('file_path')

        if not prompt:
            QMessageBox.warning(self, 'Warning', 'Please enter a prompt to improve the code.')
            return

        # Show streaming UI and disable buttons
        self.ai_tools_panel.show_streaming("Backing up and improving code...")
        self.set_status_message("Backing up original file...")
        
        # Start async improvement
        code = editor.toPlainText()
        self.controller.start_improvement(prompt, code, model, file_path)

    def on_improve_all(self):
        """Start async improvement for all open files"""
        prompt = self.ai_tools_panel.improve_input.text()
        prompt = prompt.strip()
        model = self.ai_tools_panel.model_combo.currentText()

        if not prompt:
            QMessageBox.warning(self, 'Warning', 'Please enter a prompt to improve the code.')
            return

        if self.editor_tabs.count() == 0:
            QMessageBox.warning(self, 'Warning', 'No files are currently open.')
            return

        # Show streaming UI and disable buttons
        self.ai_tools_panel.show_streaming(f"Improving {self.editor_tabs.count()} files...")
        self.set_status_message("Starting batch improvement...")
        
        # Start async improvements for all open files
        self.pending_improvements = self.editor_tabs.count()
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            code = editor.toPlainText()
            file_path = editor.property('file_path')
            self.controller.start_improvement(prompt, code, model, file_path)

    def on_loop_ia(self):
        """Start async loop improvement (5 iterations)"""
        editor = self.editor_tabs.currentWidget()
        if not editor:
            return

        prompt = self.ai_tools_panel.improve_input.text()
        prompt = prompt.strip()
        model = self.ai_tools_panel.model_combo.currentText()
        file_path = editor.property('file_path')

        if not prompt:
            QMessageBox.warning(self, 'Warning', 'Please enter a prompt to improve the code.')
            return

        # Show streaming UI and disable buttons
        self.ai_tools_panel.show_streaming("Starting AI loop (5 iterations)...")
        self.set_status_message("Starting iterative improvement...")
        
        # Start async loop improvement
        self.loop_iteration = 1
        self.loop_total = 5
        self.loop_prompt = prompt
        self.loop_model = model
        self.loop_file_path = file_path
        
        code = editor.toPlainText()
        self.controller.start_improvement(f"Iteration {self.loop_iteration}/5: {prompt}", code, model, file_path)

    def on_file_tree_double_click(self, item, column):
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if os.path.isfile(file_path):
            self.open_file_in_editor(file_path)

    def open_file_in_editor(self, file_path):
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.widget(i).property('file_path') == file_path:
                self.editor_tabs.setCurrentIndex(i)
                return

        editor = VSCTextEdit(self.controller.doc_keywords)
        with open(file_path, 'r', encoding='utf-8') as f:
            editor.setPlainText(f.read())

        tab_index = self.editor_tabs.addTab(editor, os.path.basename(file_path))
        self.editor_tabs.setCurrentIndex(tab_index)
        editor.setProperty('file_path', file_path)

    def load_snippets(self):
        """Load snippets from JSON file with version support."""
        snippets_file = os.path.join(os.path.dirname(__file__), '..', '..', 'snippets.json')
        try:
            if os.path.exists(snippets_file):
                with open(snippets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Handle legacy format (direct snippets dict)
                if isinstance(data, dict) and 'version' not in data:
                    self.snippets_data = data
                    # Migrate to new format
                    self.save_snippets()
                else:
                    # New versioned format
                    self.snippets_data = data.get('snippets', {})
            else:
                # Create default snippets
                self.snippets_data = {
                    "HTML Template": "<!DOCTYPE html>\n<html lang='en'>\n<head>\n    <meta charset='UTF-8'>\n    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n    <title>Document</title>\n</head>\n<body>\n    \n</body>\n</html>",
                    "CSS Reset": "* {\n    margin: 0;\n    padding: 0;\n    box-sizing: border-box;\n}\n\nbody {\n    font-family: Arial, sans-serif;\n    line-height: 1.6;\n}",
                    "JavaScript Function": "function functionName() {\n    // Your code here\n    return;\n}",
                    "CSS Flexbox Center": ".container {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    height: 100vh;\n}",
                    "HTML Form": "<form action='#' method='post'>\n    <label for='name'>Name:</label>\n    <input type='text' id='name' name='name' required>\n    \n    <label for='email'>Email:</label>\n    <input type='email' id='email' name='email' required>\n    \n    <button type='submit'>Submit</button>\n</form>",
                    "CSS Grid Layout": ".grid-container {\n    display: grid;\n    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n    gap: 20px;\n    padding: 20px;\n}"
                }
                self.save_snippets()
            
            self.update_snippets_list()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', f'Failed to load snippets: {str(e)}')
            self.snippets_data = {}
    
    def save_snippets(self):
        """Save snippets to JSON file with version field for future schema changes."""
        snippets_file = os.path.join(os.path.dirname(__file__), '..', '..', 'snippets.json')
        try:
            # Prepare data with versioning
            snippets_with_version = {
                "version": "1.0",
                "snippets": self.snippets_data,
                "created_at": datetime.datetime.now().isoformat(),
                "last_modified": datetime.datetime.now().isoformat()
            }
            
            with open(snippets_file, 'w', encoding='utf-8') as f:
                json.dump(snippets_with_version, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(self, 'Warning', f'Failed to save snippets: {str(e)}')
    
    def update_snippets_list(self):
        """Update the snippets list widget."""
        self.snippets_panel.clear()
        for name, code in self.snippets_data.items():
            # Show first line as preview
            preview = code.split('\n')[0][:50]
            if len(code.split('\n')[0]) > 50:
                preview += '...'
            item_text = f"{name}\n{preview}"
            self.snippets_panel.addItem(item_text)
    
    def on_add_snippet(self):
        """Add a new snippet with enhanced dialog."""
        current_editor = self.editor_tabs.currentWidget()
        if current_editor:
            # Get selected text or first few lines as default content
            cursor = current_editor.textCursor()
            if cursor.hasSelection():
                default_code = cursor.selectedText()
            else:
                default_code = current_editor.toPlainText()
        else:
            default_code = ""
        
        # Show enhanced snippet dialog
        dialog = EnhancedSnippetDialog(self, default_code)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            code = dialog.get_code()
            
            if name and code:
                # Check for duplicates and handle them
                if self._handle_snippet_duplicate(name, code):
                    self.save_snippets()
                    self.update_snippets_list()
                    QMessageBox.information(self, 'Success', f'Snippet "{name}" added successfully!')
    
    def on_remove_snippet(self):
        """Remove the selected snippet."""
        current_item = self.snippets_panel.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Warning', 'Please select a snippet to remove.')
            return
        
        # Extract snippet name from the item text
        item_text = current_item.text()
        snippet_name = item_text.split('\n')[0]
        
        reply = QMessageBox.question(
            self, 'Confirm Removal',
            f'Are you sure you want to remove the snippet "{snippet_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if snippet_name in self.snippets_data:
                del self.snippets_data[snippet_name]
                self.save_snippets()
                self.update_snippets_list()
                QMessageBox.information(self, 'Success', f'Snippet "{snippet_name}" removed successfully!')
    
    def on_insert_snippet(self):
        """Insert the selected snippet into the current editor."""
        current_item = self.snippets_panel.currentItem()
        if not current_item:
            QMessageBox.warning(self, 'Warning', 'Please select a snippet to insert.')
            return
        
        # Extract snippet name from the item text
        item_text = current_item.text()
        snippet_name = item_text.split('\n')[0]
        
        if snippet_name not in self.snippets_data:
            QMessageBox.warning(self, 'Warning', 'Snippet not found.')
            return
        
        # Get current editor
        current_editor = self.editor_tabs.currentWidget()
        if not current_editor:
            QMessageBox.warning(self, 'Warning', 'No editor tab is currently open.')
            return
        
        # Insert snippet at cursor position
        snippet_code = self.snippets_data[snippet_name]
        cursor = current_editor.textCursor()
        cursor.insertText(snippet_code)
        
        QMessageBox.information(self, 'Success', f'Snippet "{snippet_name}" inserted successfully!')
    
    def analyze_code(self):
        """Analyze current code and show problems."""
        current_editor = self.editor_tabs.currentWidget()
        if not current_editor:
            return
        
        # Clear existing problems
        self.problems_panel.clear()
        
        code = current_editor.toPlainText()
        lines = code.split('\n')
        
        # Simple static analysis
        problems = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for common issues
            if 'var ' in line and 'let ' not in line and 'const ' not in line:
                problems.append(f"Line {i}: Consider using 'let' or 'const' instead of 'var'")
            
            if line_stripped.endswith(';') and ('if ' in line or 'for ' in line or 'while ' in line):
                problems.append(f"Line {i}: Control structure shouldn't end with semicolon")
            
            if '==' in line and '===' not in line:
                problems.append(f"Line {i}: Consider using '===' for strict equality")
            
            if 'console.log' in line:
                problems.append(f"Line {i}: Remove console.log statement before production")
            
            if len(line) > 120:
                problems.append(f"Line {i}: Line too long ({len(line)} characters)")
            
            # Check for missing alt text in img tags
            if '<img' in line and 'alt=' not in line:
                problems.append(f"Line {i}: Image missing alt attribute for accessibility")
        
        # Add problems to the panel
        if problems:
            for problem in problems:
                self.problems_panel.addItem(f"⚠️ {problem}")
        else:
            self.problems_panel.addItem("✅ No issues found")

    def close_editor_tab(self, index):
        widget = self.editor_tabs.widget(index)
        widget.deleteLater()
        self.editor_tabs.removeTab(index)

    # New AI Tools Panel slots
    def on_request_improve(self, prompt, model):
        """Handle improvement request with streaming support"""
        editor = self.editor_tabs.currentWidget()
        if not editor:
            QMessageBox.warning(self, 'Warning', 'No editor tab is currently open.')
            return

        if not prompt:
            QMessageBox.warning(self, 'Warning', 'Please enter a prompt to improve the code.')
            return

        # Show streaming UI
        self.ai_tools_panel.show_streaming("Improving code...")
        
        # Add to history
        import datetime
        timestamp = datetime.datetime.now()
        self.ai_tools_panel.add_history_entry(timestamp, prompt, model)
        
        try:
            code = editor.toPlainText()
            improved_code = self.controller.improve_code(prompt, code, model)
            editor.setPlainText(improved_code)
            
            # Auto-save if enabled
            if self.ai_tools_panel.is_auto_save_enabled():
                file_path = editor.property('file_path')
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(improved_code)
                    
            self.ai_tools_panel.status_label.setText("Improvement completed!")
            QTimer.singleShot(2000, self.ai_tools_panel.hide_streaming)  # Hide after 2 seconds
            
        except Exception as e:
            self.ai_tools_panel.hide_streaming()
            QMessageBox.critical(self, 'Error', f'Failed to improve code: {str(e)}')

    def on_restore_history(self, entry_id):
        """Restore a previous improvement from history"""
        # This would need to be implemented with actual history storage
        # For now, just show a placeholder message
        QMessageBox.information(self, 'History', f'Would restore history entry: {entry_id}')
        # TODO: Implement actual history restoration logic
        
    def on_save_as_snippet(self, text_content=None):
        """Save selected text or whole file as a snippet with AI-generated smart naming"""
        current_editor = self.editor_tabs.currentWidget()
        if not current_editor:
            QMessageBox.warning(self, 'Warning', 'No editor tab is currently open.')
            return
            
        # Get content to save
        if text_content:
            content = text_content
        else:
            cursor = current_editor.textCursor()
            if cursor.hasSelection():
                content = cursor.selectedText()
            else:
                content = current_editor.toPlainText()
                
        if not content.strip():
            QMessageBox.warning(self, 'Warning', 'No content to save as snippet.')
            return
        
        # Get last improvement prompt for smart naming
        last_prompt = getattr(self.ai_tools_panel, 'last_prompt', '')
        
        # Show enhanced snippet dialog with smart naming
        dialog = EnhancedSnippetDialog(self, content, last_prompt)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            code = dialog.get_code()
            
            if name and code:
                # Check for duplicates and handle them
                if self._handle_snippet_duplicate(name, code):
                    self.save_snippets()
                    self.update_snippets_list()
                    QMessageBox.information(self, 'Success', f'Content saved as snippet "{name}"!')
    
    def set_status_message(self, message):
        """Set status bar message"""
        self.status_bar.showMessage(message)
    
    def auto_save_enabled(self):
        """Check if auto-save is enabled"""
        return self.ai_tools_panel.is_auto_save_enabled()
    
    def on_improvement_started(self, file_path):
        """Handle improvement started signal"""
        self.set_status_message(f"Starting improvement for {os.path.basename(file_path) if file_path else 'current file'}...")
    
    def on_token_received(self, file_path, token):
        """Handle streaming token received"""
        # Find the editor for this file and update with streaming content
        editor = self.find_editor_by_file_path(file_path)
        if editor:
            self.highlight_streaming_insertion(editor, token)
    
    def on_improvement_finished(self, file_path, full_code):
        """Handle improvement finished signal"""
        editor = self.find_editor_by_file_path(file_path)
        if editor:
            # Set the complete improved code
            editor.setPlainText(full_code)
            self.clear_streaming_highlights(editor)
            
            # Auto-save if enabled
            if self.auto_save_enabled() and file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(full_code)
                    self.set_status_message(f"Saved to {os.path.basename(file_path)}")
                except Exception as e:
                    self.set_status_message(f"Error saving: {str(e)}")
            else:
                self.set_status_message("Improvement completed")
            
            # Auto-add to snippets if enabled
            if self.ai_tools_panel.is_add_to_snippets_enabled():
                self._auto_save_improved_code_as_snippet(full_code)
        
        # Handle batch improvements
        if hasattr(self, 'pending_improvements') and self.pending_improvements > 0:
            self.pending_improvements -= 1
            if self.pending_improvements == 0:
                self.ai_tools_panel.hide_streaming()
                self.set_status_message("All files improved successfully")
                QMessageBox.information(self, 'Success', 'All files improved with AI.')
                return
        
        # Handle loop improvements
        if hasattr(self, 'loop_iteration') and self.loop_iteration > 0:
            if self.loop_iteration < self.loop_total:
                self.loop_iteration += 1
                self.set_status_message(f"Starting iteration {self.loop_iteration}/{self.loop_total}...")
                self.controller.start_improvement(
                    f"Iteration {self.loop_iteration}/5: {self.loop_prompt}", 
                    full_code, 
                    self.loop_model, 
                    self.loop_file_path
                )
                return
            else:
                # Loop completed
                self.loop_iteration = 0
                self.ai_tools_panel.hide_streaming()
                self.set_status_message("AI loop completed (5 iterations)")
                QMessageBox.information(self, 'Success', 'AI loop completed (5 iterations).')
                return
        
        # Single improvement completed
        self.ai_tools_panel.hide_streaming()
        self.update_preview()
    
    def on_improvement_error(self, file_path, error_message):
        """Handle improvement error signal"""
        self.ai_tools_panel.hide_streaming()
        self.set_status_message(f"Error: {error_message}")
        QMessageBox.critical(self, "Error", f"Improvement failed: {error_message}")
        
        # Reset loop state if in loop mode
        if hasattr(self, 'loop_iteration'):
            self.loop_iteration = 0
        
        # Reset batch state if in batch mode
        if hasattr(self, 'pending_improvements'):
            self.pending_improvements = 0
    
    def find_editor_by_file_path(self, file_path):
        """Find editor widget by file path"""
        if not file_path:
            # If no file path, return current editor
            return self.editor_tabs.currentWidget()
        
        for i in range(self.editor_tabs.count()):
            editor = self.editor_tabs.widget(i)
            if editor.property('file_path') == file_path:
                return editor
        return None
    
    def highlight_streaming_insertion(self, editor, token):
        """Highlight current token insertion with green background for ephemeral effect"""
        if not hasattr(editor, '_streaming_content'):
            editor._streaming_content = ""
        
        # Add token to streaming content
        editor._streaming_content += token
        
        # Get current cursor position
        cursor = editor.textCursor()
        current_pos = cursor.position()
        
        # Move to end and insert token with highlighting
        cursor.movePosition(cursor.MoveOperation.End)
        
        # Create highlight format for new token
        from PyQt6.QtGui import QTextCharFormat, QColor
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor('#90EE90'))  # Light green background
        
        # Insert token with highlight
        cursor.insertText(token, highlight_format)
        
        # Schedule removal of highlight after short delay
        QTimer.singleShot(200, lambda: self.remove_token_highlight(editor, cursor.position() - len(token), len(token)))
    
    def remove_token_highlight(self, editor, start_pos, length):
        """Remove highlighting from a token after ephemeral effect"""
        cursor = editor.textCursor()
        cursor.setPosition(start_pos)
        cursor.setPosition(start_pos + length, cursor.MoveMode.KeepAnchor)
        
        # Reset format to default
        default_format = QTextCharFormat()
        cursor.setCharFormat(default_format)
    
    def clear_streaming_highlights(self, editor):
        """Clear all streaming highlights from editor"""
        if hasattr(editor, '_streaming_content'):
            delattr(editor, '_streaming_content')
    
    def _handle_snippet_duplicate(self, name, code):
        """Handle duplicate snippet names with user confirmation"""
        if name in self.snippets_data:
            reply = QMessageBox.question(
                self, 'Duplicate Snippet Name',
                f'A snippet named "{name}" already exists. Do you want to overwrite it?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.snippets_data[name] = code
                return True
            else:
                return False
        else:
            self.snippets_data[name] = code
            return True
    
    def _auto_save_improved_code_as_snippet(self, improved_code):
        """Automatically save improved code as snippet with smart naming"""
        if not improved_code.strip():
            return
        
        # Get last prompt for smart naming
        last_prompt = getattr(self.ai_tools_panel, 'last_prompt', '')
        
        # Create smart name suggestions
        dialog = EnhancedSnippetDialog(self, improved_code, last_prompt)
        
        # Auto-fill and save without showing dialog (silent save)
        # Get the smart suggested name
        suggestions = self._get_smart_suggestions_for_code(improved_code, last_prompt)
        
        if suggestions:
            snippet_name = suggestions[0]  # Use first suggestion
            
            # Check for duplicates silently
            if snippet_name in self.snippets_data:
                # Add timestamp to make it unique
                timestamp = datetime.datetime.now().strftime("%H%M%S")
                snippet_name = f"{snippet_name} ({timestamp})"
            
            # Save snippet silently
            self.snippets_data[snippet_name] = improved_code
            self.save_snippets()
            self.update_snippets_list()
            
            # Show brief notification
            self.set_status_message(f"✅ Automatically saved as snippet: {snippet_name}")
            QTimer.singleShot(3000, lambda: self.set_status_message("Ready"))  # Clear after 3 seconds
    
    def _get_smart_suggestions_for_code(self, code, last_prompt):
        """Get smart name suggestions for code - extracted from EnhancedSnippetDialog logic"""
        suggestions = []
        
        # Suggestion 1: Based on last prompt
        if last_prompt:
            prompt_suggestion = self._extract_name_from_prompt(last_prompt)
            if prompt_suggestion:
                suggestions.append(prompt_suggestion)
        
        # Suggestion 2: Based on first line of code
        first_line_suggestion = self._extract_name_from_first_line(code)
        if first_line_suggestion:
            suggestions.append(first_line_suggestion)
        
        # Suggestion 3: Based on code analysis
        analysis_suggestion = self._analyze_code_for_name(code)
        if analysis_suggestion:
            suggestions.append(analysis_suggestion)
        
        # Suggestion 4: Generic based on code type
        type_suggestion = self._get_type_based_name(code)
        if type_suggestion:
            suggestions.append(type_suggestion)
        
        return suggestions[:1]  # Return only the first/best suggestion
    
    def _extract_name_from_prompt(self, prompt):
        """Extract meaningful name from improvement prompt"""
        # Clean and extract key words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        meaningful_words = [w for w in words if w not in [
            'the', 'and', 'for', 'with', 'add', 'make', 'create', 'build', 'improve',
            'fix', 'update', 'change', 'modify', 'enhance', 'optimize', 'this', 'that',
            'code', 'function', 'method', 'class', 'component'
        ]]
        
        if meaningful_words:
            # Take first 2-3 meaningful words
            name_words = meaningful_words[:3]
            return ' '.join(name_words).title()
        return None
    
    def _extract_name_from_first_line(self, code):
        """Extract name from first line of code"""
        if not code.strip():
            return None
        
        first_line = code.split('\n')[0].strip()
        
        # HTML tag
        html_match = re.search(r'<(\w+)', first_line)
        if html_match:
            tag = html_match.group(1)
            return f"{tag.upper()} Element"
        
        # CSS selector
        css_match = re.search(r'\.(\w+)|#(\w+)|(\w+)\s*{', first_line)
        if css_match:
            name = css_match.group(1) or css_match.group(2) or css_match.group(3)
            return f"{name.title()} Style"
        
        # JavaScript function
        js_func_match = re.search(r'function\s+(\w+)', first_line)
        if js_func_match:
            return f"{js_func_match.group(1).title()} Function"
        
        # JavaScript const/let/var
        js_var_match = re.search(r'(?:const|let|var)\s+(\w+)', first_line)
        if js_var_match:
            return f"{js_var_match.group(1).title()} Variable"
        
        return None
    
    def _analyze_code_for_name(self, code):
        """Analyze code content to suggest a name"""
        if not code.strip():
            return None
        
        code_lower = code.lower()
        
        # Check for specific patterns
        if 'flexbox' in code_lower or 'display: flex' in code_lower:
            return "Flexbox Layout"
        
        if 'grid' in code_lower or 'display: grid' in code_lower:
            return "Grid Layout"
        
        if 'animation' in code_lower or '@keyframes' in code_lower:
            return "CSS Animation"
        
        if 'form' in code_lower and '<form' in code_lower:
            return "HTML Form"
        
        if 'button' in code_lower and 'onclick' in code_lower:
            return "Interactive Button"
        
        if 'fetch(' in code_lower or 'axios' in code_lower:
            return "API Request"
        
        if 'addEventListener' in code_lower:
            return "Event Handler"
        
        return None
    
    def _get_type_based_name(self, code):
        """Get generic name based on code type"""
        if not code.strip():
            return "Empty Snippet"
        
        code_lower = code.lower()
        
        if code.strip().startswith('<!doctype html') or '<html' in code_lower:
            return "HTML Template"
        
        if code.strip().startswith('<') and '>' in code:
            return "HTML Element"
        
        if '{' in code and '}' in code and ('.' in code or '#' in code):
            return "CSS Rule"
        
        if 'function' in code_lower or '=>' in code or 'const' in code_lower:
            return "JavaScript Code"
        
        return "Code Snippet"


class EnhancedSnippetDialog(QDialog):
    """Enhanced dialog for creating snippets with smart naming and validation"""
    
    def __init__(self, parent=None, default_code="", last_prompt=""):
        super().__init__(parent)
        self.default_code = default_code
        self.last_prompt = last_prompt
        self.setup_ui()
        self.propose_smart_name()
    
    def setup_ui(self):
        self.setWindowTitle('Save as Snippet')
        self.setMinimumSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background: #1a1a1a;
                color: #e6e6e6;
            }
            QLabel {
                color: #e6e6e6;
                font-weight: 500;
            }
            QLineEdit {
                background: #2a2a2a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #10a37f;
            }
            QTextEdit {
                background: #1a1a1a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QPushButton {
                background: #10a37f;
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #0d8f73;
            }
            QPushButton:pressed {
                background: #0a7862;
            }
            QPushButton[objectName="cancel"] {
                background: #404040;
            }
            QPushButton[objectName="cancel"]:hover {
                background: #4a4a4a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Header
        header = QLabel('💾 Save Code as Snippet')
        header.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #10a37f; margin-bottom: 8px;")
        layout.addWidget(header)
        
        # Smart name suggestion section
        name_section = QFrame()
        name_section.setStyleSheet("""
            QFrame {
                background: #252525;
                border-radius: 8px;
                padding: 12px;
                margin: 4px 0;
            }
        """)
        name_layout = QVBoxLayout(name_section)
        
        name_label = QLabel('🎯 Snippet Name:')
        name_label.setStyleSheet("color: #e6e6e6; font-weight: 600;")
        name_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Enter a descriptive name for your snippet...')
        name_layout.addWidget(self.name_input)
        
        # Smart suggestions
        suggestions_label = QLabel('💡 Smart Suggestions:')
        suggestions_label.setStyleSheet("color: #999; font-size: 11px; margin-top: 8px;")
        name_layout.addWidget(suggestions_label)
        
        self.suggestions_layout = QHBoxLayout()
        name_layout.addLayout(self.suggestions_layout)
        
        layout.addWidget(name_section)
        
        # Code preview section
        code_label = QLabel('📄 Code Preview:')
        code_label.setStyleSheet("color: #e6e6e6; font-weight: 600;")
        layout.addWidget(code_label)
        
        self.code_edit = QTextEdit()
        self.code_edit.setPlainText(self.default_code)
        self.code_edit.setMaximumHeight(200)
        layout.addWidget(self.code_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton('💾 Save Snippet')
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton('❌ Cancel')
        self.cancel_button.setObjectName("cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
    
    def propose_smart_name(self):
        """Generate smart name suggestions based on code content and last prompt"""
        suggestions = []
        
        # Clear existing suggestions
        for i in reversed(range(self.suggestions_layout.count())):
            child = self.suggestions_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Suggestion 1: Based on last prompt
        if self.last_prompt:
            prompt_suggestion = self._extract_name_from_prompt(self.last_prompt)
            if prompt_suggestion:
                suggestions.append(prompt_suggestion)
        
        # Suggestion 2: Based on first line of code
        first_line_suggestion = self._extract_name_from_first_line(self.default_code)
        if first_line_suggestion:
            suggestions.append(first_line_suggestion)
        
        # Suggestion 3: Based on code analysis
        analysis_suggestion = self._analyze_code_for_name(self.default_code)
        if analysis_suggestion:
            suggestions.append(analysis_suggestion)
        
        # Suggestion 4: Generic based on code type
        type_suggestion = self._get_type_based_name(self.default_code)
        if type_suggestion:
            suggestions.append(type_suggestion)
        
        # Create suggestion buttons
        for suggestion in suggestions[:4]:  # Limit to 4 suggestions
            btn = QPushButton(suggestion)
            btn.setStyleSheet("""
                QPushButton {
                    background: #3a3a3a;
                    color: #e6e6e6;
                    border: 1px solid #4a4a4a;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background: #4a4a4a;
                    border-color: #10a37f;
                }
            """)
            btn.clicked.connect(lambda checked, name=suggestion: self.name_input.setText(name))
            self.suggestions_layout.addWidget(btn)
        
        # Set first suggestion as default
        if suggestions:
            self.name_input.setText(suggestions[0])
    
    def _extract_name_from_prompt(self, prompt):
        """Extract meaningful name from improvement prompt"""
        # Clean and extract key words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        meaningful_words = [w for w in words if w not in [
            'the', 'and', 'for', 'with', 'add', 'make', 'create', 'build', 'improve',
            'fix', 'update', 'change', 'modify', 'enhance', 'optimize', 'this', 'that',
            'code', 'function', 'method', 'class', 'component'
        ]]
        
        if meaningful_words:
            # Take first 2-3 meaningful words
            name_words = meaningful_words[:3]
            return ' '.join(name_words).title()
        return None
    
    def _extract_name_from_first_line(self, code):
        """Extract name from first line of code"""
        if not code.strip():
            return None
        
        first_line = code.split('\n')[0].strip()
        
        # HTML tag
        html_match = re.search(r'<(\w+)', first_line)
        if html_match:
            tag = html_match.group(1)
            return f"{tag.upper()} Element"
        
        # CSS selector
        css_match = re.search(r'\.(\w+)|#(\w+)|(\w+)\s*{', first_line)
        if css_match:
            name = css_match.group(1) or css_match.group(2) or css_match.group(3)
            return f"{name.title()} Style"
        
        # JavaScript function
        js_func_match = re.search(r'function\s+(\w+)', first_line)
        if js_func_match:
            return f"{js_func_match.group(1).title()} Function"
        
        # JavaScript const/let/var
        js_var_match = re.search(r'(?:const|let|var)\s+(\w+)', first_line)
        if js_var_match:
            return f"{js_var_match.group(1).title()} Variable"
        
        return None
    
    def _analyze_code_for_name(self, code):
        """Analyze code content to suggest a name"""
        if not code.strip():
            return None
        
        code_lower = code.lower()
        
        # Check for specific patterns
        if 'flexbox' in code_lower or 'display: flex' in code_lower:
            return "Flexbox Layout"
        
        if 'grid' in code_lower or 'display: grid' in code_lower:
            return "Grid Layout"
        
        if 'animation' in code_lower or '@keyframes' in code_lower:
            return "CSS Animation"
        
        if 'form' in code_lower and '<form' in code_lower:
            return "HTML Form"
        
        if 'button' in code_lower and 'onclick' in code_lower:
            return "Interactive Button"
        
        if 'fetch(' in code_lower or 'axios' in code_lower:
            return "API Request"
        
        if 'addEventListener' in code_lower:
            return "Event Handler"
        
        return None
    
    def _get_type_based_name(self, code):
        """Get generic name based on code type"""
        if not code.strip():
            return "Empty Snippet"
        
        code_lower = code.lower()
        
        if code.strip().startswith('<!doctype html') or '<html' in code_lower:
            return "HTML Template"
        
        if code.strip().startswith('<') and '>' in code:
            return "HTML Element"
        
        if '{' in code and '}' in code and ('.' in code or '#' in code):
            return "CSS Rule"
        
        if 'function' in code_lower or '=>' in code or 'const' in code_lower:
            return "JavaScript Code"
        
        return "Code Snippet"
    
    def get_name(self):
        """Get the entered snippet name"""
        return self.name_input.text().strip()
    
    def get_code(self):
        """Get the code content"""
        return self.code_edit.toPlainText().strip()
