"""
Smart Templates System
Provides intelligent code templates, project scaffolding, and snippet management.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import re

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QListWidget, QListWidgetItem, QTabWidget,
    QGroupBox, QScrollArea, QFrame, QCheckBox, QSpinBox, QFileDialog,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QTreeWidget,
    QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

class TemplateVariable:
    """Represents a template variable with metadata"""
    
    def __init__(self, name: str, description: str = "", default_value: str = "", 
                 var_type: str = "string", options: List[str] = None):
        self.name = name
        self.description = description
        self.default_value = default_value
        self.var_type = var_type  # string, number, boolean, choice, file, folder
        self.options = options or []

class CodeTemplate:
    """Represents a code template with variables and metadata"""
    
    def __init__(self, id: str, name: str, description: str, content: str,
                 language: str = "", category: str = "General", 
                 variables: List[TemplateVariable] = None,
                 files: Dict[str, str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.content = content
        self.language = language
        self.category = category
        self.variables = variables or []
        self.files = files or {}  # For multi-file templates
        self.created_at = datetime.now().isoformat()
        self.usage_count = 0

class ProjectTemplate:
    """Represents a complete project template"""
    
    def __init__(self, id: str, name: str, description: str, 
                 framework: str = "", structure: Dict = None,
                 dependencies: List[str] = None,
                 variables: List[TemplateVariable] = None):
        self.id = id
        self.name = name
        self.description = description
        self.framework = framework
        self.structure = structure or {}  # Directory/file structure
        self.dependencies = dependencies or []
        self.variables = variables or []
        self.created_at = datetime.now().isoformat()

class VariableInputDialog(QDialog):
    """Dialog for inputting template variables"""
    
    def __init__(self, variables: List[TemplateVariable], parent=None):
        super().__init__(parent)
        self.variables = variables
        self.values = {}
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Template Variables")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Scroll area for variables
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.form_layout = QFormLayout(scroll_widget)
        
        self.input_widgets = {}
        
        for var in self.variables:
            label = QLabel(f"{var.name}:")
            if var.description:
                label.setToolTip(var.description)
            
            if var.var_type == "string":
                widget = QLineEdit()
                widget.setText(var.default_value)
                widget.textChanged.connect(lambda text, v=var: self.update_value(v.name, text))
            
            elif var.var_type == "number":
                widget = QSpinBox()
                widget.setRange(0, 9999)
                widget.setValue(int(var.default_value) if var.default_value.isdigit() else 0)
                widget.valueChanged.connect(lambda value, v=var: self.update_value(v.name, str(value)))
            
            elif var.var_type == "boolean":
                widget = QCheckBox()
                widget.setChecked(var.default_value.lower() == "true")
                widget.toggled.connect(lambda checked, v=var: self.update_value(v.name, str(checked).lower()))
            
            elif var.var_type == "choice":
                widget = QComboBox()
                widget.addItems(var.options)
                if var.default_value in var.options:
                    widget.setCurrentText(var.default_value)
                widget.currentTextChanged.connect(lambda text, v=var: self.update_value(v.name, text))
            
            elif var.var_type == "file":
                widget = QWidget()
                widget_layout = QHBoxLayout(widget)
                widget_layout.setContentsMargins(0, 0, 0, 0)
                line_edit = QLineEdit()
                line_edit.setText(var.default_value)
                browse_btn = QPushButton("Browse...")
                browse_btn.clicked.connect(lambda _, le=line_edit, v=var: self.browse_file(le, v))
                widget_layout.addWidget(line_edit)
                widget_layout.addWidget(browse_btn)
                line_edit.textChanged.connect(lambda text, v=var: self.update_value(v.name, text))
            
            elif var.var_type == "folder":
                widget = QWidget()
                widget_layout = QHBoxLayout(widget)
                widget_layout.setContentsMargins(0, 0, 0, 0)
                line_edit = QLineEdit()
                line_edit.setText(var.default_value)
                browse_btn = QPushButton("Browse...")
                browse_btn.clicked.connect(lambda _, le=line_edit, v=var: self.browse_folder(le, v))
                widget_layout.addWidget(line_edit)
                widget_layout.addWidget(browse_btn)
                line_edit.textChanged.connect(lambda text, v=var: self.update_value(v.name, text))
            
            else:
                widget = QLineEdit()
                widget.setText(var.default_value)
                widget.textChanged.connect(lambda text, v=var: self.update_value(v.name, text))
            
            self.input_widgets[var.name] = widget
            self.form_layout.addRow(label, widget)
            
            # Initialize value
            self.update_value(var.name, var.default_value)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def update_value(self, name: str, value: str):
        """Update variable value"""
        self.values[name] = value
    
    def browse_file(self, line_edit: QLineEdit, var: TemplateVariable):
        """Browse for file"""
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select {var.name}")
        if file_path:
            line_edit.setText(file_path)
    
    def browse_folder(self, line_edit: QLineEdit, var: TemplateVariable):
        """Browse for folder"""
        folder_path = QFileDialog.getExistingDirectory(self, f"Select {var.name}")
        if folder_path:
            line_edit.setText(folder_path)
    
    def get_values(self) -> Dict[str, str]:
        """Get all variable values"""
        return self.values.copy()

class TemplateProcessor:
    """Processes templates with variable substitution"""
    
    @staticmethod
    def process_content(content: str, variables: Dict[str, str]) -> str:
        """Process template content with variable substitution"""
        processed = content
        
        for var_name, var_value in variables.items():
            # Support multiple placeholder formats
            patterns = [
                f"{{{{{var_name}}}}}",  # {{variable}}
                f"${{{var_name}}}",     # ${variable}
                f"<{var_name}>",        # <variable>
            ]
            
            for pattern in patterns:
                processed = processed.replace(pattern, var_value)
        
        # Process special placeholders
        processed = TemplateProcessor.process_special_placeholders(processed)
        
        return processed
    
    @staticmethod
    def process_special_placeholders(content: str) -> str:
        """Process special placeholders like date, time, etc."""
        now = datetime.now()
        
        replacements = {
            "{{DATE}}": now.strftime("%Y-%m-%d"),
            "{{TIME}}": now.strftime("%H:%M:%S"),
            "{{DATETIME}}": now.strftime("%Y-%m-%d %H:%M:%S"),
            "{{YEAR}}": str(now.year),
            "{{MONTH}}": str(now.month),
            "{{DAY}}": str(now.day),
            "{{UUID}}": str(uuid.uuid4()),
            "{{CURSOR}}": "",  # Placeholder for cursor position
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)
        
        return content
    
    @staticmethod
    def extract_variables(content: str) -> List[str]:
        """Extract variable names from template content"""
        patterns = [
            r"\{\{(\w+)\}\}",  # {{variable}}
            r"\$\{(\w+)\}",    # ${variable}
            r"<(\w+)>",        # <variable>
        ]
        
        variables = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            variables.update(matches)
        
        # Remove special placeholders
        special = {"DATE", "TIME", "DATETIME", "YEAR", "MONTH", "DAY", "UUID", "CURSOR"}
        variables = variables - special
        
        return list(variables)

class SmartTemplatesWidget(QWidget):
    """Main widget for smart templates management"""
    
    template_applied = pyqtSignal(str, str)  # content, language
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.code_templates: List[CodeTemplate] = []
        self.project_templates: List[ProjectTemplate] = []
        self.templates_file = "templates.json"
        self.setup_ui()
        self.load_templates()
        self.load_default_templates()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget for different template types
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Code Templates Tab
        self.setup_code_templates_tab()
        
        # Project Templates Tab
        self.setup_project_templates_tab()
        
        # Custom Templates Tab
        self.setup_custom_templates_tab()
    
    def setup_code_templates_tab(self):
        """Setup code templates tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All", "HTML", "CSS", "JavaScript", "Python", "General"])
        self.category_filter.currentTextChanged.connect(self.filter_code_templates)
        filter_layout.addWidget(self.category_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Templates list
        self.code_templates_list = QListWidget()
        self.code_templates_list.itemDoubleClicked.connect(self.apply_code_template)
        layout.addWidget(self.code_templates_list)
        
        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Consolas", 10))
        preview_layout.addWidget(self.code_preview)
        layout.addWidget(preview_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply Template")
        apply_btn.clicked.connect(self.apply_selected_code_template)
        buttons_layout.addWidget(apply_btn)
        
        edit_btn = QPushButton("Edit Template")
        edit_btn.clicked.connect(self.edit_selected_code_template)
        buttons_layout.addWidget(edit_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.tab_widget.addTab(tab, "Code Templates")
    
    def setup_project_templates_tab(self):
        """Setup project templates tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Framework filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Framework:"))
        self.framework_filter = QComboBox()
        self.framework_filter.addItems(["All", "React", "Vue", "Angular", "Express", "Flask", "Django"])
        self.framework_filter.currentTextChanged.connect(self.filter_project_templates)
        filter_layout.addWidget(self.framework_filter)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Templates list
        self.project_templates_list = QListWidget()
        self.project_templates_list.itemDoubleClicked.connect(self.create_project_from_template)
        layout.addWidget(self.project_templates_list)
        
        # Structure preview
        preview_group = QGroupBox("Project Structure")
        preview_layout = QVBoxLayout(preview_group)
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabel("Files and Folders")
        preview_layout.addWidget(self.structure_tree)
        layout.addWidget(preview_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        create_btn = QPushButton("Create Project")
        create_btn.clicked.connect(self.create_selected_project)
        buttons_layout.addWidget(create_btn)
        
        customize_btn = QPushButton("Customize & Create")
        customize_btn.clicked.connect(self.customize_and_create_project)
        buttons_layout.addWidget(customize_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.tab_widget.addTab(tab, "Project Templates")
    
    def setup_custom_templates_tab(self):
        """Setup custom templates management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Template editor
        editor_group = QGroupBox("Create/Edit Template")
        editor_layout = QFormLayout(editor_group)
        
        self.template_name = QLineEdit()
        editor_layout.addRow("Name:", self.template_name)
        
        self.template_description = QLineEdit()
        editor_layout.addRow("Description:", self.template_description)
        
        self.template_category = QComboBox()
        self.template_category.setEditable(True)
        self.template_category.addItems(["HTML", "CSS", "JavaScript", "Python", "General"])
        editor_layout.addRow("Category:", self.template_category)
        
        self.template_content = QTextEdit()
        self.template_content.setFont(QFont("Consolas", 10))
        self.template_content.setPlaceholderText("Enter template content with variables: {{variable_name}}")
        editor_layout.addRow("Content:", self.template_content)
        
        # Variables section
        variables_group = QGroupBox("Variables")
        variables_layout = QVBoxLayout(variables_group)
        
        self.variables_list = QListWidget()
        variables_layout.addWidget(self.variables_list)
        
        var_buttons = QHBoxLayout()
        add_var_btn = QPushButton("Add Variable")
        add_var_btn.clicked.connect(self.add_template_variable)
        var_buttons.addWidget(add_var_btn)
        
        remove_var_btn = QPushButton("Remove Variable")
        remove_var_btn.clicked.connect(self.remove_template_variable)
        var_buttons.addWidget(remove_var_btn)
        
        var_buttons.addStretch()
        variables_layout.addLayout(var_buttons)
        
        editor_layout.addRow(variables_group)
        layout.addWidget(editor_group)
        
        # Save/Load buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save Template")
        save_btn.clicked.connect(self.save_custom_template)
        buttons_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Template")
        load_btn.clicked.connect(self.load_custom_template)
        buttons_layout.addWidget(load_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_template_editor)
        buttons_layout.addWidget(clear_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.tab_widget.addTab(tab, "Custom Templates")
    
    def load_default_templates(self):
        """Load default templates"""
        default_code_templates = [
            CodeTemplate(
                "html5_basic", "HTML5 Basic Structure", "Basic HTML5 document structure",
                """<!DOCTYPE html>
<html lang="{{language}}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
</head>
<body>
    {{CURSOR}}
</body>
</html>""",
                "html", "HTML",
                [
                    TemplateVariable("language", "Document language", "en"),
                    TemplateVariable("title", "Page title", "New Page")
                ]
            ),
            
            CodeTemplate(
                "react_component", "React Function Component", "React functional component template",
                """import React from 'react';

interface {{component_name}}Props {
    // Define props here
}

const {{component_name}}: React.FC<{{component_name}}Props> = (props) => {
    return (
        <div className="{{class_name}}">
            {{CURSOR}}
        </div>
    );
};

export default {{component_name}};""",
                "javascript", "React",
                [
                    TemplateVariable("component_name", "Component name", "MyComponent"),
                    TemplateVariable("class_name", "CSS class name", "my-component")
                ]
            ),
            
            CodeTemplate(
                "css_flexbox", "CSS Flexbox Layout", "Flexbox layout template",
                """.{{container_class}} {
    display: flex;
    justify-content: {{justify}};
    align-items: {{align}};
    flex-direction: {{direction}};
    gap: {{gap}};
}

.{{item_class}} {
    flex: {{flex}};
}""",
                "css", "CSS",
                [
                    TemplateVariable("container_class", "Container class", "flex-container"),
                    TemplateVariable("item_class", "Item class", "flex-item"),
                    TemplateVariable("justify", "Justify content", "center", "choice", 
                                   ["flex-start", "center", "flex-end", "space-between", "space-around"]),
                    TemplateVariable("align", "Align items", "center", "choice",
                                   ["flex-start", "center", "flex-end", "stretch"]),
                    TemplateVariable("direction", "Flex direction", "row", "choice",
                                   ["row", "column", "row-reverse", "column-reverse"]),
                    TemplateVariable("gap", "Gap size", "1rem"),
                    TemplateVariable("flex", "Flex value", "1")
                ]
            ),
            
            CodeTemplate(
                "js_async_function", "JavaScript Async Function", "Async function template",
                """async function {{function_name}}({{parameters}}) {
    try {
        {{CURSOR}}
        return result;
    } catch (error) {
        console.error('Error in {{function_name}}:', error);
        throw error;
    }
}""",
                "javascript", "JavaScript",
                [
                    TemplateVariable("function_name", "Function name", "fetchData"),
                    TemplateVariable("parameters", "Function parameters", "url")
                ]
            )
        ]
        
        self.code_templates.extend(default_code_templates)
        self.update_code_templates_list()
    
    def filter_code_templates(self, category: str):
        """Filter code templates by category"""
        self.update_code_templates_list(category)
    
    def update_code_templates_list(self, category_filter: str = "All"):
        """Update the code templates list"""
        self.code_templates_list.clear()
        
        for template in self.code_templates:
            if category_filter == "All" or template.category == category_filter:
                item = QListWidgetItem(f"{template.name} - {template.description}")
                item.setData(Qt.ItemDataRole.UserRole, template)
                self.code_templates_list.addItem(item)
    
    def apply_code_template(self, item: QListWidgetItem):
        """Apply a code template"""
        template = item.data(Qt.ItemDataRole.UserRole)
        if template and template.variables:
            dialog = VariableInputDialog(template.variables, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                variables = dialog.get_values()
                content = TemplateProcessor.process_content(template.content, variables)
                self.template_applied.emit(content, template.language)
                template.usage_count += 1
        else:
            content = TemplateProcessor.process_special_placeholders(template.content)
            self.template_applied.emit(content, template.language)
            template.usage_count += 1
    
    def apply_selected_code_template(self):
        """Apply the currently selected code template"""
        current_item = self.code_templates_list.currentItem()
        if current_item:
            self.apply_code_template(current_item)
    
    def edit_selected_code_template(self):
        """Edit the currently selected code template"""
        current_item = self.code_templates_list.currentItem()
        if current_item:
            template = current_item.data(Qt.ItemDataRole.UserRole)
            self.load_template_for_editing(template)
            self.tab_widget.setCurrentIndex(2)  # Switch to custom templates tab
    
    def load_template_for_editing(self, template: CodeTemplate):
        """Load a template into the editor"""
        self.template_name.setText(template.name)
        self.template_description.setText(template.description)
        self.template_category.setCurrentText(template.category)
        self.template_content.setPlainText(template.content)
        
        # Load variables
        self.variables_list.clear()
        for var in template.variables:
            item = QListWidgetItem(f"{var.name} ({var.var_type}): {var.description}")
            item.setData(Qt.ItemDataRole.UserRole, var)
            self.variables_list.addItem(item)
    
    def add_template_variable(self):
        """Add a new template variable"""
        # Simple implementation - could be enhanced with a dialog
        var_name, ok = QLineEdit.getText(self, "Variable Name", "Enter variable name:")
        if ok and var_name:
            var = TemplateVariable(var_name, f"Description for {var_name}", "")
            item = QListWidgetItem(f"{var.name} ({var.var_type}): {var.description}")
            item.setData(Qt.ItemDataRole.UserRole, var)
            self.variables_list.addItem(item)
    
    def remove_template_variable(self):
        """Remove selected template variable"""
        current_item = self.variables_list.currentItem()
        if current_item:
            self.variables_list.takeItem(self.variables_list.row(current_item))
    
    def save_custom_template(self):
        """Save the custom template"""
        name = self.template_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a template name.")
            return
        
        # Collect variables
        variables = []
        for i in range(self.variables_list.count()):
            item = self.variables_list.item(i)
            var = item.data(Qt.ItemDataRole.UserRole)
            variables.append(var)
        
        template = CodeTemplate(
            id=str(uuid.uuid4()),
            name=name,
            description=self.template_description.text(),
            content=self.template_content.toPlainText(),
            category=self.template_category.currentText(),
            language=self.template_category.currentText().lower(),
            variables=variables
        )
        
        self.code_templates.append(template)
        self.update_code_templates_list()
        self.save_templates()
        
        QMessageBox.information(self, "Success", "Template saved successfully!")
        self.clear_template_editor()
    
    def clear_template_editor(self):
        """Clear the template editor"""
        self.template_name.clear()
        self.template_description.clear()
        self.template_content.clear()
        self.variables_list.clear()
    
    def save_templates(self):
        """Save templates to file"""
        try:
            data = {
                "code_templates": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "description": t.description,
                        "content": t.content,
                        "language": t.language,
                        "category": t.category,
                        "variables": [
                            {
                                "name": v.name,
                                "description": v.description,
                                "default_value": v.default_value,
                                "var_type": v.var_type,
                                "options": v.options
                            } for v in t.variables
                        ],
                        "created_at": t.created_at,
                        "usage_count": t.usage_count
                    } for t in self.code_templates
                ],
                "project_templates": []  # TODO: Implement project templates serialization
            }
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving templates: {e}")
    
    def load_templates(self):
        """Load templates from file"""
        try:
            if os.path.exists(self.templates_file):
                with open(self.templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load code templates
                for t_data in data.get("code_templates", []):
                    variables = []
                    for v_data in t_data.get("variables", []):
                        var = TemplateVariable(
                            v_data["name"],
                            v_data["description"],
                            v_data["default_value"],
                            v_data["var_type"],
                            v_data["options"]
                        )
                        variables.append(var)
                    
                    template = CodeTemplate(
                        t_data["id"],
                        t_data["name"],
                        t_data["description"],
                        t_data["content"],
                        t_data["language"],
                        t_data["category"],
                        variables
                    )
                    template.created_at = t_data.get("created_at", "")
                    template.usage_count = t_data.get("usage_count", 0)
                    self.code_templates.append(template)
        except Exception as e:
            print(f"Error loading templates: {e}")
    
    # Project template methods (placeholder implementations)
    def filter_project_templates(self, framework: str):
        """Filter project templates by framework"""
        pass
    
    def create_project_from_template(self, item: QListWidgetItem):
        """Create project from template"""
        pass
    
    def create_selected_project(self):
        """Create project from selected template"""
        pass
    
    def customize_and_create_project(self):
        """Customize and create project"""
        pass
    
    def load_custom_template(self):
        """Load a custom template from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Template", "", "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                # Load template data into editor
                self.template_name.setText(template_data.get("name", ""))
                self.template_description.setText(template_data.get("description", ""))
                self.template_content.setPlainText(template_data.get("content", ""))
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load template: {e}")
