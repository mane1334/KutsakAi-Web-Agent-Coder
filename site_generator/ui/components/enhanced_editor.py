"""
Enhanced Code Editor
Provides advanced code editing capabilities with syntax highlighting,
IntelliSense, multiple cursors, and professional features.
"""

import os
import re
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum

from PyQt6.QtWidgets import (
    QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCompleter, QScrollBar, QFrame, QTextEdit, QApplication
)
from PyQt6.QtCore import Qt, QRect, QSize, QTimer, pyqtSignal, QStringListModel
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QTextCursor, QTextDocument, QTextCharFormat,
    QSyntaxHighlighter, QTextBlock, QKeySequence, QShortcut, QPalette,
    QFontMetrics, QTextOption
)

class Language(Enum):
    """Supported programming languages"""
    HTML = "html"
    CSS = "css"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    JSON = "json"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "text"

class SyntaxTheme:
    """Syntax highlighting themes"""
    
    DARK_THEME = {
        'background': '#1e1e1e',
        'foreground': '#d4d4d4',
        'selection': '#264f78',
        'line_number': '#858585',
        'current_line': '#282828',
        'keyword': '#569cd6',
        'string': '#ce9178',
        'comment': '#6a9955',
        'number': '#b5cea8',
        'operator': '#d4d4d4',
        'function': '#dcdcaa',
        'class': '#4ec9b0',
        'tag': '#569cd6',
        'attribute': '#92c5f8',
        'value': '#ce9178',
        'error': '#f44747',
        'warning': '#ffcc02'
    }
    
    LIGHT_THEME = {
        'background': '#ffffff',
        'foreground': '#000000',
        'selection': '#add6ff',
        'line_number': '#237893',
        'current_line': '#f5f5f5',
        'keyword': '#0000ff',
        'string': '#a31515',
        'comment': '#008000',
        'number': '#098658',
        'operator': '#000000',
        'function': '#795e26',
        'class': '#267f99',
        'tag': '#800000',
        'attribute': '#ff0000',
        'value': '#0451a5',
        'error': '#cd3131',
        'warning': '#bf8803'
    }

class AdvancedSyntaxHighlighter(QSyntaxHighlighter):
    """Advanced syntax highlighter with multiple language support"""
    
    def __init__(self, document: QTextDocument, language: Language = Language.PLAIN_TEXT, 
                 theme: Dict = None):
        super().__init__(document)
        self.language = language
        self.theme = theme or SyntaxTheme.DARK_THEME
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        """Setup highlighting rules based on language"""
        self.highlighting_rules = []
        
        if self.language == Language.PYTHON:
            self.setup_python_rules()
        elif self.language == Language.JAVASCRIPT:
            self.setup_javascript_rules()
        elif self.language == Language.HTML:
            self.setup_html_rules()
        elif self.language == Language.CSS:
            self.setup_css_rules()
        elif self.language == Language.JSON:
            self.setup_json_rules()
        elif self.language == Language.MARKDOWN:
            self.setup_markdown_rules()
    
    def setup_python_rules(self):
        """Setup Python syntax highlighting rules"""
        # Keywords
        python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if',
            'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'raise',
            'return', 'try', 'while', 'with', 'yield', 'async', 'await'
        ]
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        for word in python_keywords:
            self.highlighting_rules.append((
                re.compile(r'\b' + word + r'\b'),
                keyword_format
            ))
        
        # Built-ins
        builtins = [
            'bool', 'int', 'float', 'str', 'list', 'dict', 'tuple', 'set',
            'len', 'range', 'enumerate', 'zip', 'map', 'filter', 'sum',
            'min', 'max', 'abs', 'round', 'print', 'input', 'open'
        ]
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor(self.theme['function']))
        
        for builtin in builtins:
            self.highlighting_rules.append((
                re.compile(r'\b' + builtin + r'\b'),
                builtin_format
            ))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.extend([
            (re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format),
            (re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format),
            (re.compile(r'""".*?"""'), string_format),
            (re.compile(r"'''.*?'''"), string_format),
        ])
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            re.compile(r'#[^\r\n]*'),
            comment_format
        ))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((
            re.compile(r'\b\d+\.?\d*\b'),
            number_format
        ))
        
        # Functions and classes
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(self.theme['function']))
        self.highlighting_rules.extend([
            (re.compile(r'\bdef\s+(\w+)'), function_format),
            (re.compile(r'\bclass\s+(\w+)'), QTextCharFormat())
        ])
    
    def setup_javascript_rules(self):
        """Setup JavaScript syntax highlighting rules"""
        # Keywords
        js_keywords = [
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
            'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
            'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof',
            'var', 'void', 'while', 'with', 'yield', 'async', 'await'
        ]
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        for word in js_keywords:
            self.highlighting_rules.append((
                re.compile(r'\b' + word + r'\b'),
                keyword_format
            ))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.extend([
            (re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format),
            (re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format),
            (re.compile(r'`[^`\\]*(\\.[^`\\]*)*`'), string_format),
        ])
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.extend([
            (re.compile(r'//[^\r\n]*'), comment_format),
            (re.compile(r'/\*.*?\*/'), comment_format),
        ])
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((
            re.compile(r'\b\d+\.?\d*\b'),
            number_format
        ))
    
    def setup_html_rules(self):
        """Setup HTML syntax highlighting rules"""
        # Tags
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(self.theme['tag']))
        tag_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            re.compile(r'<[!?/]?\w+'),
            tag_format
        ))
        
        # Attributes
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(QColor(self.theme['attribute']))
        self.highlighting_rules.append((
            re.compile(r'\b\w+(?=\s*=)'),
            attribute_format
        ))
        
        # Attribute values
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(self.theme['value']))
        self.highlighting_rules.extend([
            (re.compile(r'"[^"]*"'), value_format),
            (re.compile(r"'[^']*'"), value_format),
        ])
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            re.compile(r'<!--.*?-->'),
            comment_format
        ))
    
    def setup_css_rules(self):
        """Setup CSS syntax highlighting rules"""
        # Selectors
        selector_format = QTextCharFormat()
        selector_format.setForeground(QColor(self.theme['tag']))
        self.highlighting_rules.extend([
            (re.compile(r'[.#]?\w+(?=\s*{)'), selector_format),
            (re.compile(r'[.#]\w+'), selector_format),
        ])
        
        # Properties
        property_format = QTextCharFormat()
        property_format.setForeground(QColor(self.theme['attribute']))
        self.highlighting_rules.append((
            re.compile(r'\b[\w-]+(?=\s*:)'),
            property_format
        ))
        
        # Values
        value_format = QTextCharFormat()
        value_format.setForeground(QColor(self.theme['value']))
        self.highlighting_rules.extend([
            (re.compile(r'"[^"]*"'), value_format),
            (re.compile(r"'[^']*'"), value_format),
            (re.compile(r'\b\d+(\.\d+)?(px|em|rem|%|vh|vw|pt)\b'), value_format),
        ])
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            re.compile(r'/\*.*?\*/'),
            comment_format
        ))
    
    def setup_json_rules(self):
        """Setup JSON syntax highlighting rules"""
        # Keys
        key_format = QTextCharFormat()
        key_format.setForeground(QColor(self.theme['attribute']))
        self.highlighting_rules.append((
            re.compile(r'"[^"]*"(?=\s*:)'),
            key_format
        ))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(self.theme['string']))
        self.highlighting_rules.append((
            re.compile(r'"[^"]*"(?!\s*:)'),
            string_format
        ))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(self.theme['number']))
        self.highlighting_rules.append((
            re.compile(r'\b\d+\.?\d*\b'),
            number_format
        ))
        
        # Booleans and null
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(self.theme['keyword']))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        for word in ['true', 'false', 'null']:
            self.highlighting_rules.append((
                re.compile(r'\b' + word + r'\b'),
                keyword_format
            ))
    
    def setup_markdown_rules(self):
        """Setup Markdown syntax highlighting rules"""
        # Headers
        header_format = QTextCharFormat()
        header_format.setForeground(QColor(self.theme['keyword']))
        header_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((
            re.compile(r'^#{1,6}.*$'),
            header_format
        ))
        
        # Bold
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.extend([
            (re.compile(r'\*\*[^*]+\*\*'), bold_format),
            (re.compile(r'__[^_]+__'), bold_format),
        ])
        
        # Italic
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.extend([
            (re.compile(r'\*[^*]+\*'), italic_format),
            (re.compile(r'_[^_]+_'), italic_format),
        ])
        
        # Code
        code_format = QTextCharFormat()
        code_format.setForeground(QColor(self.theme['string']))
        code_format.setFontFamily('Consolas')
        self.highlighting_rules.extend([
            (re.compile(r'`[^`]+`'), code_format),
            (re.compile(r'```[^`]*```'), code_format),
        ])
        
        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(QColor(self.theme['function']))
        link_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        self.highlighting_rules.extend([
            (re.compile(r'\[([^\]]+)\]\([^)]+\)'), link_format),
            (re.compile(r'https?://[^\s]+'), link_format),
        ])
    
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text"""
        # Apply highlighting rules
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)
        
        # Handle multi-line comments for languages that support them
        if self.language in [Language.JAVASCRIPT, Language.CSS]:
            self.highlight_multiline_comments(text)
    
    def highlight_multiline_comments(self, text: str):
        """Handle multi-line comments"""
        start_pattern = re.compile(r'/\*')
        end_pattern = re.compile(r'\*/')
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(self.theme['comment']))
        comment_format.setFontItalic(True)
        
        # Check if we're continuing a multi-line comment from previous block
        if self.previousBlockState() == 1:
            start_index = 0
        else:
            start_match = start_pattern.search(text)
            start_index = start_match.start() if start_match else -1
        
        while start_index >= 0:
            end_match = end_pattern.search(text, start_index)
            if end_match:
                end_index = end_match.end()
                comment_length = end_index - start_index
                self.setFormat(start_index, comment_length, comment_format)
                start_match = start_pattern.search(text, end_index)
                start_index = start_match.start() if start_match else -1
            else:
                # Comment continues to next block
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
                self.setFormat(start_index, comment_length, comment_format)
                break

class LineNumberArea(QWidget):
    """Widget for displaying line numbers"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
    
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class IntelliSenseProvider:
    """Provides IntelliSense suggestions based on context"""
    
    def __init__(self, language: Language):
        self.language = language
        self.keywords = self.get_language_keywords()
        self.builtin_functions = self.get_builtin_functions()
        self.snippets = self.get_language_snippets()
    
    def get_language_keywords(self) -> List[str]:
        """Get keywords for the current language"""
        keywords_map = {
            Language.PYTHON: [
                'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
                'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if',
                'import', 'in', 'is', 'lambda', 'not', 'or', 'pass', 'raise',
                'return', 'try', 'while', 'with', 'yield', 'async', 'await',
                'bool', 'int', 'float', 'str', 'list', 'dict', 'tuple', 'set'
            ],
            Language.JAVASCRIPT: [
                'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
                'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
                'for', 'function', 'if', 'import', 'in', 'instanceof', 'let', 'new',
                'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof',
                'var', 'void', 'while', 'with', 'yield', 'async', 'await'
            ],
            Language.HTML: [
                'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th',
                'form', 'input', 'button', 'select', 'option', 'textarea',
                'head', 'body', 'html', 'title', 'meta', 'link', 'script', 'style'
            ],
            Language.CSS: [
                'color', 'background', 'margin', 'padding', 'border', 'display',
                'flex', 'grid', 'font-size', 'font-family', 'width', 'height',
                'position', 'absolute', 'relative', 'fixed', 'float', 'clear',
                'overflow', 'z-index', 'align-items', 'justify-content'
            ]
        }
        return keywords_map.get(self.language, [])
    
    def get_builtin_functions(self) -> List[str]:
        """Get built-in functions for the current language"""
        functions_map = {
            Language.PYTHON: [
                'len', 'range', 'enumerate', 'zip', 'map', 'filter', 'sum',
                'min', 'max', 'abs', 'round', 'print', 'input', 'open',
                'type', 'isinstance', 'hasattr', 'getattr', 'setattr'
            ],
            Language.JAVASCRIPT: [
                'console.log', 'parseInt', 'parseFloat', 'isNaN', 'setTimeout',
                'setInterval', 'clearTimeout', 'clearInterval', 'JSON.parse',
                'JSON.stringify', 'Object.keys', 'Object.values', 'Array.from'
            ]
        }
        return functions_map.get(self.language, [])
    
    def get_language_snippets(self) -> Dict[str, str]:
        """Get language-specific snippets"""
        snippets_map = {
            Language.PYTHON: {
                'if': 'if ${condition}:\n    ${cursor}',
                'for': 'for ${item} in ${iterable}:\n    ${cursor}',
                'def': 'def ${function_name}(${parameters}):\n    ${cursor}',
                'class': 'class ${ClassName}:\n    def __init__(self):\n        ${cursor}'
            },
            Language.JAVASCRIPT: {
                'if': 'if (${condition}) {\n    ${cursor}\n}',
                'for': 'for (let ${i} = 0; ${i} < ${length}; ${i}++) {\n    ${cursor}\n}',
                'function': 'function ${name}(${parameters}) {\n    ${cursor}\n}',
                'arrow': '(${parameters}) => {\n    ${cursor}\n}'
            },
            Language.HTML: {
                'div': '<div class="${class}">\n    ${cursor}\n</div>',
                'a': '<a href="${url}">${text}</a>',
                'img': '<img src="${src}" alt="${alt}">',
                'form': '<form action="${action}" method="${method}">\n    ${cursor}\n</form>'
            }
        }
        return snippets_map.get(self.language, {})
    
    def get_suggestions(self, text: str, cursor_position: int) -> List[str]:
        """Get IntelliSense suggestions for the current context"""
        # Extract current word
        current_word = self.extract_current_word(text, cursor_position)
        
        # Combine all possible suggestions
        all_suggestions = (
            self.keywords + 
            self.builtin_functions + 
            list(self.snippets.keys()) +
            self.extract_document_words(text)
        )
        
        # Filter suggestions based on current word
        if current_word:
            suggestions = [s for s in all_suggestions if s.startswith(current_word)]
        else:
            suggestions = all_suggestions
        
        # Sort by relevance
        suggestions.sort(key=lambda x: (
            0 if x in self.keywords else
            1 if x in self.builtin_functions else
            2 if x in self.snippets else 3
        ))
        
        return suggestions[:20]  # Limit to top 20 suggestions
    
    def extract_current_word(self, text: str, cursor_position: int) -> str:
        """Extract the word at cursor position"""
        start = cursor_position
        while start > 0 and text[start - 1].isalnum():
            start -= 1
        
        end = cursor_position
        while end < len(text) and text[end].isalnum():
            end += 1
        
        return text[start:cursor_position]
    
    def extract_document_words(self, text: str) -> List[str]:
        """Extract unique words from the document"""
        words = re.findall(r'\b\w{3,}\b', text)  # Words with 3+ characters
        return list(set(words))

class EnhancedCodeEditor(QPlainTextEdit):
    """Enhanced code editor with advanced features"""
    
    cursor_position_changed = pyqtSignal(int, int)  # line, column
    language_changed = pyqtSignal(Language)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Editor properties
        self.current_language = Language.PLAIN_TEXT
        self.current_theme = SyntaxTheme.DARK_THEME
        self.show_line_numbers = True
        self.current_line_highlighting = True
        self.word_wrap_enabled = False
        
        # Components
        self.line_number_area = LineNumberArea(self)
        self.syntax_highlighter = None
        self.intellisense_provider = None
        self.completer = None
        
        # Multiple cursors support
        self.additional_cursors: List[QTextCursor] = []
        self.selection_mode = False
        
        # Auto-completion
        self.completion_timer = QTimer()
        self.completion_timer.setSingleShot(True)
        self.completion_timer.timeout.connect(self.show_completion)
        
        self.setup_editor()
        self.setup_signals()
        self.setup_shortcuts()
        self.apply_theme()
    
    def setup_editor(self):
        """Setup basic editor properties"""
        # Font
        font = QFont("Consolas", 12)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Tab settings
        font_metrics = QFontMetrics(font)
        tab_width = font_metrics.horizontalAdvance(' ') * 4
        self.setTabStopDistance(tab_width)
        
        # Line wrap
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Cursor
        self.setCursorWidth(2)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    
    def setup_signals(self):
        """Setup signal connections"""
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self.emit_cursor_position)
        self.textChanged.connect(self.on_text_changed)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Multiple cursors
        QShortcut(QKeySequence("Ctrl+D"), self, self.select_next_occurrence)
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, self.select_all_occurrences)
        QShortcut(QKeySequence("Alt+Click"), self, self.add_cursor_at_position)
        
        # Code formatting
        QShortcut(QKeySequence("Shift+Alt+F"), self, self.format_document)
        
        # Navigation
        QShortcut(QKeySequence("Ctrl+G"), self, self.go_to_line)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, self.go_to_symbol)
        
        # Comments
        QShortcut(QKeySequence("Ctrl+/"), self, self.toggle_line_comment)
        QShortcut(QKeySequence("Ctrl+Shift+/"), self, self.toggle_block_comment)
    
    def apply_theme(self):
        """Apply the current theme"""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(self.current_theme['background']))
        palette.setColor(QPalette.ColorRole.Text, QColor(self.current_theme['foreground']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(self.current_theme['selection']))
        self.setPalette(palette)
        
        # Update line number area
        self.update_line_number_area_width()
        self.update()
    
    def set_language(self, language: Language):
        """Set the programming language for syntax highlighting"""
        self.current_language = language
        
        # Setup syntax highlighter
        if self.syntax_highlighter:
            self.syntax_highlighter.setDocument(None)
        
        self.syntax_highlighter = AdvancedSyntaxHighlighter(
            self.document(), language, self.current_theme
        )
        
        # Setup IntelliSense
        self.intellisense_provider = IntelliSenseProvider(language)
        self.setup_completer()
        
        self.language_changed.emit(language)
    
    def setup_completer(self):
        """Setup auto-completion"""
        if self.intellisense_provider:
            suggestions = self.intellisense_provider.get_suggestions("", 0)
            model = QStringListModel(suggestions)
            
            self.completer = QCompleter(model, self)
            self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.completer.setWidget(self)
            self.completer.activated.connect(self.insert_completion)
    
    def on_text_changed(self):
        """Handle text changes"""
        # Trigger auto-completion after a delay
        self.completion_timer.stop()
        self.completion_timer.start(300)  # 300ms delay
    
    def show_completion(self):
        """Show auto-completion popup"""
        if not self.intellisense_provider or not self.completer:
            return
        
        cursor = self.textCursor()
        text = self.toPlainText()
        suggestions = self.intellisense_provider.get_suggestions(text, cursor.position())
        
        if suggestions:
            model = QStringListModel(suggestions)
            self.completer.setModel(model)
            
            # Position completion popup
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(200)
            self.completer.complete(cursor_rect)
    
    def insert_completion(self, completion: str):
        """Insert auto-completion text"""
        cursor = self.textCursor()
        
        # Remove partial word
        current_word = self.intellisense_provider.extract_current_word(
            self.toPlainText(), cursor.position()
        )
        
        if current_word:
            cursor.movePosition(QTextCursor.MoveOperation.Left, 
                              QTextCursor.MoveMode.KeepAnchor, len(current_word))
            cursor.removeSelectedText()
        
        # Insert completion
        if completion in self.intellisense_provider.snippets:
            snippet = self.intellisense_provider.snippets[completion]
            self.insert_snippet(snippet)
        else:
            cursor.insertText(completion)
    
    def insert_snippet(self, snippet: str):
        """Insert a code snippet with placeholder support"""
        cursor = self.textCursor()
        
        # Replace placeholders (simplified implementation)
        processed_snippet = snippet.replace('${cursor}', '')
        cursor.insertText(processed_snippet)
        
        # Position cursor at placeholder (if any)
        cursor_pos = snippet.find('${cursor}')
        if cursor_pos != -1:
            new_pos = cursor.position() - (len(snippet) - cursor_pos)
            cursor.setPosition(new_pos)
            self.setTextCursor(cursor)
    
    def select_next_occurrence(self):
        """Select next occurrence of current word (Ctrl+D)"""
        cursor = self.textCursor()
        
        if not cursor.hasSelection():
            # Select current word
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            self.setTextCursor(cursor)
        else:
            # Find next occurrence
            selected_text = cursor.selectedText()
            document = self.document()
            
            # Search from current position
            next_cursor = document.find(selected_text, cursor.selectionEnd())
            if next_cursor.isNull():
                # Search from beginning
                next_cursor = document.find(selected_text, 0)
            
            if not next_cursor.isNull():
                self.additional_cursors.append(cursor)
                self.setTextCursor(next_cursor)
    
    def select_all_occurrences(self):
        """Select all occurrences of current word (Ctrl+Shift+D)"""
        cursor = self.textCursor()
        
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            document = self.document()
            
            # Find all occurrences
            self.additional_cursors.clear()
            search_cursor = document.find(selected_text, 0)
            
            while not search_cursor.isNull():
                if search_cursor.position() != cursor.position():
                    self.additional_cursors.append(search_cursor)
                search_cursor = document.find(selected_text, search_cursor.selectionEnd())
    
    def add_cursor_at_position(self):
        """Add cursor at clicked position (Alt+Click)"""
        # This would be triggered by mouse events
        pass
    
    def format_document(self):
        """Format the entire document"""
        # Basic implementation - could be enhanced with language-specific formatters
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        text = cursor.selectedText()
        formatted_text = self.basic_format(text)
        
        cursor.insertText(formatted_text)
    
    def basic_format(self, text: str) -> str:
        """Basic text formatting"""
        lines = text.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Adjust indent level based on brackets
            if any(char in stripped for char in ['}', ']', ')']):
                indent_level = max(0, indent_level - 1)
            
            # Add indentation
            formatted_line = '    ' * indent_level + stripped
            formatted_lines.append(formatted_line)
            
            # Increase indent for opening brackets
            if any(char in stripped for char in ['{', '[', '(']):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    def go_to_line(self):
        """Go to specific line number"""
        # This would show a dialog to input line number
        pass
    
    def go_to_symbol(self):
        """Go to symbol (function, class, etc.)"""
        # This would show a dialog with available symbols
        pass
    
    def toggle_line_comment(self):
        """Toggle line comment"""
        cursor = self.textCursor()
        
        # Get comment string for current language
        comment_chars = {
            Language.PYTHON: '#',
            Language.JAVASCRIPT: '//',
            Language.CSS: '/*',
            Language.HTML: '<!--'
        }
        
        comment_char = comment_chars.get(self.current_language, '#')
        
        # Toggle comment for current line or selection
        if cursor.hasSelection():
            self.toggle_selection_comment(cursor, comment_char)
        else:
            self.toggle_single_line_comment(cursor, comment_char)
    
    def toggle_single_line_comment(self, cursor: QTextCursor, comment_char: str):
        """Toggle comment for a single line"""
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        
        line_text = cursor.selectedText()
        
        if line_text.strip().startswith(comment_char):
            # Remove comment
            new_text = line_text.replace(comment_char + ' ', '', 1)
            new_text = new_text.replace(comment_char, '', 1)
        else:
            # Add comment
            indent = len(line_text) - len(line_text.lstrip())
            new_text = line_text[:indent] + comment_char + ' ' + line_text[indent:]
        
        cursor.insertText(new_text)
    
    def toggle_selection_comment(self, cursor: QTextCursor, comment_char: str):
        """Toggle comment for selected lines"""
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        start_line = cursor.blockNumber()
        
        cursor.setPosition(end)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        end_line = cursor.blockNumber()
        
        # Process each line
        for line_num in range(start_line, end_line + 1):
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down, 
                              QTextCursor.MoveMode.MoveAnchor, line_num)
            self.toggle_single_line_comment(cursor, comment_char)
    
    def toggle_block_comment(self):
        """Toggle block comment"""
        # Implementation for block comments
        pass
    
    def line_number_area_width(self) -> int:
        """Calculate line number area width"""
        if not self.show_line_numbers:
            return 0
        
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self):
        """Update line number area width"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect: QRect, dy: int):
        """Update line number area when scrolling"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                        self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Paint line numbers"""
        if not self.show_line_numbers:
            return
        
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(self.current_theme['background']).darker(110))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        painter.setPen(QColor(self.current_theme['line_number']))
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, top, self.line_number_area.width() - 3, 
                               self.fontMetrics().height(), 
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
    
    def highlight_current_line(self):
        """Highlight the current line"""
        if not self.current_line_highlighting:
            return
        
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.current_theme['current_line'])
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def emit_cursor_position(self):
        """Emit cursor position change signal"""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)
    
    def set_theme(self, theme: Dict):
        """Set editor theme"""
        self.current_theme = theme
        self.apply_theme()
        
        if self.syntax_highlighter:
            self.syntax_highlighter.theme = theme
            self.syntax_highlighter.setup_highlighting_rules()
            self.syntax_highlighter.rehighlight()
    
    def toggle_line_numbers(self):
        """Toggle line number visibility"""
        self.show_line_numbers = not self.show_line_numbers
        self.update_line_number_area_width()
        self.update()
    
    def toggle_word_wrap(self):
        """Toggle word wrap"""
        self.word_wrap_enabled = not self.word_wrap_enabled
        if self.word_wrap_enabled:
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
