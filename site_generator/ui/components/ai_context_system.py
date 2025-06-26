"""
AI Context Awareness System
Provides intelligent code suggestions, context-aware completions,
and AI-powered development assistance.
"""

import os
import json
import re
import ast
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QPushButton,
    QProgressBar, QTabWidget, QListWidget, QListWidgetItem, QFrame,
    QScrollArea, QGroupBox, QCheckBox, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor

# Simulated AI client (replace with actual AI service)
class AIClient:
    """Interface for AI services (OpenAI, local models, etc.)"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.cache = {}
    
    def generate_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Generate code suggestions based on context"""
        # Cache key based on context hash
        cache_key = hashlib.md5(str(context).encode()).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Simulate AI response (replace with actual AI call)
        suggestions = self._simulate_ai_response(context)
        self.cache[cache_key] = suggestions
        
        return suggestions
    
    def _simulate_ai_response(self, context: Dict[str, Any]) -> List[str]:
        """Simulate AI response for demonstration"""
        language = context.get('language', 'python')
        code_type = context.get('code_type', 'function')
        current_code = context.get('current_code', '')
        
        # Pattern-based suggestions
        suggestions = []
        
        if language == 'python':
            if 'def ' in current_code:
                suggestions.extend([
                    "Add type hints to function parameters",
                    "Add docstring with parameter descriptions",
                    "Add error handling with try/except",
                    "Add input validation"
                ])
            elif 'class ' in current_code:
                suggestions.extend([
                    "Add __init__ method",
                    "Add __str__ and __repr__ methods",
                    "Add property decorators for attributes",
                    "Add type annotations"
                ])
            elif 'import ' in current_code:
                suggestions.extend([
                    "Group imports by standard, third-party, local",
                    "Add import optimization",
                    "Check for unused imports"
                ])
        
        elif language == 'javascript':
            if 'function' in current_code or '=>' in current_code:
                suggestions.extend([
                    "Add JSDoc comments",
                    "Add parameter validation",
                    "Add async/await if needed",
                    "Add error handling"
                ])
            elif 'class' in current_code:
                suggestions.extend([
                    "Add constructor method",
                    "Add getter/setter methods",
                    "Add method chaining"
                ])
        
        elif language == 'html':
            suggestions.extend([
                "Add semantic HTML5 elements",
                "Add accessibility attributes",
                "Add meta tags for SEO",
                "Add responsive design classes"
            ])
        
        elif language == 'css':
            suggestions.extend([
                "Add CSS Grid or Flexbox layout",
                "Add responsive breakpoints",
                "Add CSS custom properties",
                "Add browser prefixes"
            ])
        
        return suggestions[:5]  # Limit to top 5 suggestions

@dataclass
class CodeContext:
    """Represents the current code context"""
    language: str
    file_path: str
    current_line: int
    current_column: int
    selected_text: str
    surrounding_code: str
    project_files: List[str]
    dependencies: List[str]
    cursor_position: int

class ContextAnalyzer:
    """Analyzes code context for AI suggestions"""
    
    def __init__(self):
        self.language_patterns = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass'],
            'json': ['.json'],
            'markdown': ['.md', '.markdown']
        }
    
    def analyze_context(self, editor_content: str, cursor_position: int,
                       file_path: str = "", selected_text: str = "") -> CodeContext:
        """Analyze the current code context"""
        
        # Detect language
        language = self._detect_language(file_path, editor_content)
        
        # Get current line and column
        lines = editor_content[:cursor_position].split('\n')
        current_line = len(lines)
        current_column = len(lines[-1]) if lines else 0
        
        # Get surrounding code (context window)
        surrounding_code = self._get_surrounding_code(editor_content, cursor_position)
        
        # Analyze project structure (simplified)
        project_files = self._get_project_files(file_path)
        dependencies = self._extract_dependencies(editor_content, language)
        
        return CodeContext(
            language=language,
            file_path=file_path,
            current_line=current_line,
            current_column=current_column,
            selected_text=selected_text,
            surrounding_code=surrounding_code,
            project_files=project_files,
            dependencies=dependencies,
            cursor_position=cursor_position
        )
    
    def _detect_language(self, file_path: str, content: str) -> str:
        """Detect programming language from file extension or content"""
        if file_path:
            for lang, extensions in self.language_patterns.items():
                if any(file_path.endswith(ext) for ext in extensions):
                    return lang
        
        # Content-based detection
        if '<!DOCTYPE html>' in content or '<html' in content:
            return 'html'
        elif 'def ' in content or 'import ' in content:
            return 'python'
        elif 'function' in content or 'const ' in content or 'let ' in content:
            return 'javascript'
        elif '{' in content and '}' in content and ':' in content:
            return 'css'
        
        return 'text'
    
    def _get_surrounding_code(self, content: str, cursor_position: int, 
                            window_size: int = 500) -> str:
        """Get code around cursor position"""
        start = max(0, cursor_position - window_size)
        end = min(len(content), cursor_position + window_size)
        return content[start:end]
    
    def _get_project_files(self, current_file: str) -> List[str]:
        """Get list of project files (simplified)"""
        if not current_file:
            return []
        
        project_dir = os.path.dirname(current_file)
        files = []
        
        try:
            for root, _, filenames in os.walk(project_dir):
                for filename in filenames:
                    if any(filename.endswith(ext) for exts in self.language_patterns.values() for ext in exts):
                        files.append(os.path.join(root, filename))
        except:
            pass
        
        return files[:50]  # Limit to 50 files
    
    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract dependencies from code"""
        dependencies = []
        
        if language == 'python':
            # Extract imports
            import_pattern = r'(?:from\s+(\S+)\s+)?import\s+([^\n]+)'
            matches = re.findall(import_pattern, content)
            for match in matches:
                if match[0]:  # from ... import
                    dependencies.append(match[0])
                else:  # import ...
                    deps = [dep.strip().split(' as ')[0] for dep in match[1].split(',')]
                    dependencies.extend(deps)
        
        elif language == 'javascript':
            # Extract imports/requires
            import_patterns = [
                r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'require\([\'"]([^\'"]+)[\'"]\)'
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)
        
        return list(set(dependencies))

class SmartCodeSuggestion:
    """Represents a smart code suggestion"""
    
    def __init__(self, text: str, description: str, confidence: float,
                 suggestion_type: str, code_snippet: str = ""):
        self.text = text
        self.description = description
        self.confidence = confidence
        self.suggestion_type = suggestion_type  # refactor, optimize, fix, enhance
        self.code_snippet = code_snippet
        self.timestamp = datetime.now()

class AIContextSystem(QObject):
    """Main AI Context Awareness System"""
    
    suggestions_ready = pyqtSignal(list)  # List of SmartCodeSuggestion
    analysis_complete = pyqtSignal(dict)  # Analysis results
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_client = AIClient()
        self.context_analyzer = ContextAnalyzer()
        self.suggestion_cache = {}
        self.analysis_timer = QTimer()
        self.analysis_timer.setSingleShot(True)
        self.analysis_timer.timeout.connect(self._perform_analysis)
        
        # Learning system
        self.user_preferences = {}
        self.suggestion_history = []
        self.accepted_suggestions = []
    
    def analyze_code_context(self, editor_content: str, cursor_position: int,
                           file_path: str = "", selected_text: str = ""):
        """Analyze code context and generate suggestions"""
        # Debounce analysis
        self.current_analysis_params = {
            'editor_content': editor_content,
            'cursor_position': cursor_position,
            'file_path': file_path,
            'selected_text': selected_text
        }
        
        self.analysis_timer.stop()
        self.analysis_timer.start(500)  # 500ms delay
    
    def _perform_analysis(self):
        """Perform the actual analysis"""
        params = self.current_analysis_params
        
        # Analyze context
        context = self.context_analyzer.analyze_context(
            params['editor_content'],
            params['cursor_position'],
            params['file_path'],
            params['selected_text']
        )
        
        # Generate AI suggestions
        ai_context = {
            'language': context.language,
            'current_code': context.surrounding_code,
            'selected_text': context.selected_text,
            'dependencies': context.dependencies,
            'file_path': context.file_path
        }
        
        suggestions_text = self.ai_client.generate_suggestions(ai_context)
        
        # Convert to SmartCodeSuggestion objects
        suggestions = []
        for i, suggestion_text in enumerate(suggestions_text):
            suggestion = SmartCodeSuggestion(
                text=suggestion_text,
                description=f"AI suggestion based on current context",
                confidence=0.8 - (i * 0.1),  # Decreasing confidence
                suggestion_type="enhance",
                code_snippet=""
            )
            suggestions.append(suggestion)
        
        # Add context-specific suggestions
        context_suggestions = self._generate_context_suggestions(context)
        suggestions.extend(context_suggestions)
        
        # Store in history
        self.suggestion_history.append({
            'timestamp': datetime.now(),
            'context': context,
            'suggestions': suggestions
        })
        
        # Emit signals
        self.suggestions_ready.emit(suggestions)
        self.analysis_complete.emit({
            'context': context,
            'suggestions_count': len(suggestions),
            'language': context.language
        })
    
    def _generate_context_suggestions(self, context: CodeContext) -> List[SmartCodeSuggestion]:
        """Generate context-specific suggestions"""
        suggestions = []
        
        # Code quality suggestions
        if context.language == 'python':
            if 'print(' in context.surrounding_code:
                suggestions.append(SmartCodeSuggestion(
                    text="Replace print statements with logging",
                    description="Use logging module for better debugging",
                    confidence=0.9,
                    suggestion_type="refactor",
                    code_snippet="import logging\nlogging.info('message')"
                ))
        
        # Performance suggestions
        if 'for' in context.surrounding_code and 'range(len(' in context.surrounding_code:
            suggestions.append(SmartCodeSuggestion(
                text="Use enumerate() instead of range(len())",
                description="More Pythonic and efficient iteration",
                confidence=0.85,
                suggestion_type="optimize",
                code_snippet="for i, item in enumerate(items):"
            ))
        
        # Security suggestions
        if context.language == 'javascript' and 'innerHTML' in context.surrounding_code:
            suggestions.append(SmartCodeSuggestion(
                text="Consider using textContent or sanitization",
                description="innerHTML can be vulnerable to XSS attacks",
                confidence=0.95,
                suggestion_type="fix",
                code_snippet="element.textContent = value;"
            ))
        
        return suggestions
    
    def accept_suggestion(self, suggestion: SmartCodeSuggestion):
        """Record that a suggestion was accepted"""
        self.accepted_suggestions.append({
            'suggestion': suggestion,
            'timestamp': datetime.now()
        })
        
        # Update user preferences based on accepted suggestions
        suggestion_type = suggestion.suggestion_type
        if suggestion_type not in self.user_preferences:
            self.user_preferences[suggestion_type] = 0
        self.user_preferences[suggestion_type] += 1
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights about user coding patterns"""
        total_suggestions = len(self.suggestion_history)
        accepted_count = len(self.accepted_suggestions)
        
        acceptance_rate = accepted_count / total_suggestions if total_suggestions > 0 else 0
        
        # Most accepted suggestion types
        type_counts = {}
        for accepted in self.accepted_suggestions:
            suggestion_type = accepted['suggestion'].suggestion_type
            type_counts[suggestion_type] = type_counts.get(suggestion_type, 0) + 1
        
        most_accepted_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        
        return {
            'total_suggestions': total_suggestions,
            'accepted_suggestions': accepted_count,
            'acceptance_rate': acceptance_rate,
            'most_accepted_type': most_accepted_type,
            'user_preferences': self.user_preferences
        }

class AIAssistantWidget(QWidget):
    """Widget for displaying AI suggestions and insights"""
    
    suggestion_accepted = pyqtSignal(object)  # SmartCodeSuggestion
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai_system = AIContextSystem()
        self.current_suggestions = []
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QGroupBox("AI Assistant")
        header_layout = QVBoxLayout(header)
        
        # Status
        self.status_label = QLabel("Ready for analysis...")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        header_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        header_layout.addWidget(self.progress_bar)
        
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Suggestions tab
        self.setup_suggestions_tab()
        self.tabs.addTab(self.suggestions_widget, "💡 Suggestions")
        
        # Insights tab
        self.setup_insights_tab()
        self.tabs.addTab(self.insights_widget, "📊 Insights")
        
        # Settings tab
        self.setup_settings_tab()
        self.tabs.addTab(self.settings_widget, "⚙️ Settings")
        
        layout.addWidget(self.tabs)
        
        # Apply modern styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #f8f9fa, stop: 1 #e9ecef);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #007bff, stop: 1 #0056b3);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #0056b3, stop: 1 #004085);
            }
            QPushButton:pressed {
                background: #004085;
            }
        """)
    
    def setup_suggestions_tab(self):
        """Setup suggestions tab"""
        self.suggestions_widget = QWidget()
        layout = QVBoxLayout(self.suggestions_widget)
        
        # Suggestions list
        self.suggestions_list = QListWidget()
        self.suggestions_list.setAlternatingRowColors(True)
        layout.addWidget(self.suggestions_list)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("✅ Apply Selected")
        self.apply_btn.clicked.connect(self.apply_selected_suggestion)
        buttons_layout.addWidget(self.apply_btn)
        
        self.dismiss_btn = QPushButton("❌ Dismiss")
        self.dismiss_btn.clicked.connect(self.dismiss_suggestion)
        buttons_layout.addWidget(self.dismiss_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh_suggestions)
        buttons_layout.addWidget(self.refresh_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
    
    def setup_insights_tab(self):
        """Setup insights tab"""
        self.insights_widget = QWidget()
        layout = QVBoxLayout(self.insights_widget)
        
        # Insights display
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.insights_layout = QVBoxLayout(scroll_widget)
        
        # Placeholder insights
        self.insights_labels = {}
        insight_types = [
            "Total Suggestions", "Accepted Suggestions", "Acceptance Rate",
            "Most Accepted Type", "Coding Patterns"
        ]
        
        for insight_type in insight_types:
            label = QLabel(f"{insight_type}: Loading...")
            label.setStyleSheet("padding: 5px; border-bottom: 1px solid #eee;")
            self.insights_labels[insight_type] = label
            self.insights_layout.addWidget(label)
        
        self.insights_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Update insights button
        update_btn = QPushButton("📈 Update Insights")
        update_btn.clicked.connect(self.update_insights)
        layout.addWidget(update_btn)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        self.settings_widget = QWidget()
        layout = QVBoxLayout(self.settings_widget)
        
        # AI Settings
        ai_group = QGroupBox("AI Settings")
        ai_layout = QVBoxLayout(ai_group)
        
        # Enable/disable AI
        self.ai_enabled_checkbox = QCheckBox("Enable AI Suggestions")
        self.ai_enabled_checkbox.setChecked(True)
        ai_layout.addWidget(self.ai_enabled_checkbox)
        
        # Suggestion frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Analysis Delay (ms):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(100, 5000)
        self.delay_spinbox.setValue(500)
        freq_layout.addWidget(self.delay_spinbox)
        freq_layout.addStretch()
        ai_layout.addLayout(freq_layout)
        
        # Confidence threshold
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Min Confidence:"))
        self.confidence_spinbox = QSpinBox()
        self.confidence_spinbox.setRange(0, 100)
        self.confidence_spinbox.setValue(70)
        self.confidence_spinbox.setSuffix("%")
        conf_layout.addWidget(self.confidence_spinbox)
        conf_layout.addStretch()
        ai_layout.addLayout(conf_layout)
        
        layout.addWidget(ai_group)
        
        # Suggestion Types
        types_group = QGroupBox("Suggestion Types")
        types_layout = QVBoxLayout(types_group)
        
        self.suggestion_type_checkboxes = {}
        suggestion_types = ["refactor", "optimize", "fix", "enhance"]
        
        for suggestion_type in suggestion_types:
            checkbox = QCheckBox(suggestion_type.title())
            checkbox.setChecked(True)
            self.suggestion_type_checkboxes[suggestion_type] = checkbox
            types_layout.addWidget(checkbox)
        
        layout.addWidget(types_group)
        
        layout.addStretch()
    
    def connect_signals(self):
        """Connect AI system signals"""
        self.ai_system.suggestions_ready.connect(self.display_suggestions)
        self.ai_system.analysis_complete.connect(self.on_analysis_complete)
    
    def analyze_context(self, editor_content: str, cursor_position: int,
                       file_path: str = "", selected_text: str = ""):
        """Trigger context analysis"""
        if self.ai_enabled_checkbox.isChecked():
            self.status_label.setText("Analyzing context...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            
            self.ai_system.analyze_code_context(
                editor_content, cursor_position, file_path, selected_text
            )
    
    def display_suggestions(self, suggestions: List[SmartCodeSuggestion]):
        """Display AI suggestions"""
        self.current_suggestions = suggestions
        self.suggestions_list.clear()
        
        min_confidence = self.confidence_spinbox.value() / 100.0
        enabled_types = [
            type_name for type_name, checkbox in self.suggestion_type_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        for suggestion in suggestions:
            if (suggestion.confidence >= min_confidence and 
                suggestion.suggestion_type in enabled_types):
                
                item_text = f"🎯 {suggestion.text}\n"
                item_text += f"   📝 {suggestion.description}\n"
                item_text += f"   🎲 Confidence: {suggestion.confidence:.0%}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, suggestion)
                
                # Color by confidence
                if suggestion.confidence >= 0.8:
                    item.setBackground(QColor("#d4edda"))  # High confidence - green
                elif suggestion.confidence >= 0.6:
                    item.setBackground(QColor("#fff3cd"))  # Medium confidence - yellow
                else:
                    item.setBackground(QColor("#f8d7da"))  # Low confidence - red
                
                self.suggestions_list.addItem(item)
        
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Found {self.suggestions_list.count()} suggestions")
    
    def on_analysis_complete(self, results: Dict[str, Any]):
        """Handle analysis completion"""
        language = results.get('language', 'unknown')
        count = results.get('suggestions_count', 0)
        
        self.status_label.setText(f"Analysis complete: {count} suggestions for {language}")
    
    def apply_selected_suggestion(self):
        """Apply the selected suggestion"""
        current_item = self.suggestions_list.currentItem()
        if current_item:
            suggestion = current_item.data(Qt.ItemDataRole.UserRole)
            self.ai_system.accept_suggestion(suggestion)
            self.suggestion_accepted.emit(suggestion)
            
            # Remove from list
            row = self.suggestions_list.row(current_item)
            self.suggestions_list.takeItem(row)
    
    def dismiss_suggestion(self):
        """Dismiss the selected suggestion"""
        current_item = self.suggestions_list.currentItem()
        if current_item:
            row = self.suggestions_list.row(current_item)
            self.suggestions_list.takeItem(row)
    
    def refresh_suggestions(self):
        """Refresh suggestions"""
        self.status_label.setText("Refreshing suggestions...")
        # This would trigger a new analysis with current context
    
    def update_insights(self):
        """Update coding insights"""
        insights = self.ai_system.get_learning_insights()
        
        self.insights_labels["Total Suggestions"].setText(
            f"Total Suggestions: {insights['total_suggestions']}"
        )
        self.insights_labels["Accepted Suggestions"].setText(
            f"Accepted Suggestions: {insights['accepted_suggestions']}"
        )
        self.insights_labels["Acceptance Rate"].setText(
            f"Acceptance Rate: {insights['acceptance_rate']:.1%}"
        )
        self.insights_labels["Most Accepted Type"].setText(
            f"Most Accepted Type: {insights['most_accepted_type'] or 'N/A'}"
        )
        
        # Patterns
        patterns = []
        for pref_type, count in insights['user_preferences'].items():
            patterns.append(f"{pref_type}: {count}")
        
        patterns_text = "Coding Patterns: " + (", ".join(patterns) if patterns else "No patterns yet")
        self.insights_labels["Coding Patterns"].setText(patterns_text)
