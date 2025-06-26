"""
Productivity Tools System
Advanced productivity features including task management, 
time tracking, and enhanced workflow tools.
"""

import os
import json
import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTextEdit, QListWidget, QListWidgetItem, QComboBox, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QGroupBox, QProgressBar,
    QDateTimeEdit, QSpinBox, QSlider, QSplitter, QFrame, QCalendarWidget,
    QScrollArea, QDialog, QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QDateTime, QDate, QTime, QThread,
    QObject, QMutex, QMutexLocker
)
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPixmap, QPainter

from .visual_enhancements import ModernButton, NotificationManager, ModernCard, ProgressIndicator

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    """Task status types"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class ProjectStatus(Enum):
    """Project status types"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"

@dataclass
class Task:
    """Task data structure"""
    id: str
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    project_id: Optional[str] = None
    tags: List[str] = None
    due_date: Optional[datetime.datetime] = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    completed_at: Optional[datetime.datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.datetime.now()

@dataclass
class Project:
    """Project data structure"""
    id: str
    name: str
    description: str = ""
    status: ProjectStatus = ProjectStatus.PLANNING
    color: str = "#2196F3"
    created_at: datetime.datetime = None
    due_date: Optional[datetime.datetime] = None
    progress: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class TimeEntry:
    """Time tracking entry"""
    id: str
    task_id: str
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    description: str = ""
    is_running: bool = False

class TaskManager(QObject):
    """Core task management system"""
    
    tasks_updated = pyqtSignal()
    projects_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.tasks: Dict[str, Task] = {}
        self.projects: Dict[str, Project] = {}
        self.time_entries: Dict[str, TimeEntry] = {}
        self.data_file = "productivity_data.json"
        self.mutex = QMutex()
        self.load_data()
    
    def generate_id(self) -> str:
        """Generate unique ID"""
        import uuid
        return str(uuid.uuid4())
    
    def add_task(self, task: Task) -> str:
        """Add a new task"""
        with QMutexLocker(self.mutex):
            if not task.id:
                task.id = self.generate_id()
            self.tasks[task.id] = task
            self.save_data()
            self.tasks_updated.emit()
            return task.id
    
    def update_task(self, task_id: str, **kwargs):
        """Update task properties"""
        with QMutexLocker(self.mutex):
            if task_id in self.tasks:
                task = self.tasks[task_id]
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                task.updated_at = datetime.datetime.now()
                if task.status == TaskStatus.DONE and not task.completed_at:
                    task.completed_at = datetime.datetime.now()
                self.save_data()
                self.tasks_updated.emit()
    
    def delete_task(self, task_id: str):
        """Delete a task"""
        with QMutexLocker(self.mutex):
            if task_id in self.tasks:
                del self.tasks[task_id]
                self.save_data()
                self.tasks_updated.emit()
    
    def add_project(self, project: Project) -> str:
        """Add a new project"""
        with QMutexLocker(self.mutex):
            if not project.id:
                project.id = self.generate_id()
            self.projects[project.id] = project
            self.save_data()
            self.projects_updated.emit()
            return project.id
    
    def update_project(self, project_id: str, **kwargs):
        """Update project properties"""
        with QMutexLocker(self.mutex):
            if project_id in self.projects:
                project = self.projects[project_id]
                for key, value in kwargs.items():
                    if hasattr(project, key):
                        setattr(project, key, value)
                self.save_data()
                self.projects_updated.emit()
    
    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Get all tasks for a project"""
        return [task for task in self.tasks.values() if task.project_id == project_id]
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by status"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.datetime.now()
        return [task for task in self.tasks.values() 
                if task.due_date and task.due_date < now and task.status != TaskStatus.DONE]
    
    def calculate_project_progress(self, project_id: str) -> float:
        """Calculate project progress based on completed tasks"""
        tasks = self.get_tasks_by_project(project_id)
        if not tasks:
            return 0.0
        
        completed = sum(1 for task in tasks if task.status == TaskStatus.DONE)
        return (completed / len(tasks)) * 100
    
    def start_time_tracking(self, task_id: str, description: str = "") -> str:
        """Start time tracking for a task"""
        entry_id = self.generate_id()
        entry = TimeEntry(
            id=entry_id,
            task_id=task_id,
            start_time=datetime.datetime.now(),
            description=description,
            is_running=True
        )
        self.time_entries[entry_id] = entry
        return entry_id
    
    def stop_time_tracking(self, entry_id: str):
        """Stop time tracking"""
        if entry_id in self.time_entries:
            entry = self.time_entries[entry_id]
            entry.end_time = datetime.datetime.now()
            entry.is_running = False
            
            # Update task actual hours
            if entry.task_id in self.tasks:
                duration = (entry.end_time - entry.start_time).total_seconds() / 3600
                self.tasks[entry.task_id].actual_hours += duration
    
    def save_data(self):
        """Save data to file"""
        try:
            data = {
                'tasks': {tid: asdict(task) for tid, task in self.tasks.items()},
                'projects': {pid: asdict(project) for pid, project in self.projects.items()},
                'time_entries': {eid: asdict(entry) for eid, entry in self.time_entries.items()}
            }
            
            # Convert datetime objects to strings
            def serialize_datetime(obj):
                if isinstance(obj, datetime.datetime):
                    return obj.isoformat()
                return obj
            
            # Serialize datetime fields
            for task_data in data['tasks'].values():
                for field in ['created_at', 'updated_at', 'completed_at', 'due_date']:
                    if task_data.get(field):
                        task_data[field] = serialize_datetime(task_data[field])
            
            for project_data in data['projects'].values():
                for field in ['created_at', 'due_date']:
                    if project_data.get(field):
                        project_data[field] = serialize_datetime(project_data[field])
            
            for entry_data in data['time_entries'].values():
                for field in ['start_time', 'end_time']:
                    if entry_data.get(field):
                        entry_data[field] = serialize_datetime(entry_data[field])
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def load_data(self):
        """Load data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                # Parse datetime fields
                def parse_datetime(date_str):
                    if date_str:
                        return datetime.datetime.fromisoformat(date_str)
                    return None
                
                # Load tasks
                for task_data in data.get('tasks', {}).values():
                    for field in ['created_at', 'updated_at', 'completed_at', 'due_date']:
                        if task_data.get(field):
                            task_data[field] = parse_datetime(task_data[field])
                    
                    task_data['priority'] = TaskPriority(task_data.get('priority', TaskPriority.MEDIUM.value))
                    task_data['status'] = TaskStatus(task_data.get('status', TaskStatus.TODO.value))
                    
                    task = Task(**task_data)
                    self.tasks[task.id] = task
                
                # Load projects
                for project_data in data.get('projects', {}).values():
                    for field in ['created_at', 'due_date']:
                        if project_data.get(field):
                            project_data[field] = parse_datetime(project_data[field])
                    
                    project_data['status'] = ProjectStatus(project_data.get('status', ProjectStatus.PLANNING.value))
                    
                    project = Project(**project_data)
                    self.projects[project.id] = project
                
                # Load time entries
                for entry_data in data.get('time_entries', {}).values():
                    for field in ['start_time', 'end_time']:
                        if entry_data.get(field):
                            entry_data[field] = parse_datetime(entry_data[field])
                    
                    entry = TimeEntry(**entry_data)
                    self.time_entries[entry.id] = entry
                    
        except Exception as e:
            print(f"Error loading data: {e}")

class TaskWidget(QFrame):
    """Widget for displaying and editing a single task"""
    
    task_updated = pyqtSignal(str)  # task_id
    task_deleted = pyqtSignal(str)  # task_id
    
    def __init__(self, task: Task, task_manager: TaskManager, parent=None):
        super().__init__(parent)
        self.task = task
        self.task_manager = task_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup task widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        
        # Header row
        header_layout = QHBoxLayout()
        
        # Checkbox for completion
        self.completed_cb = QCheckBox()
        self.completed_cb.setChecked(self.task.status == TaskStatus.DONE)
        self.completed_cb.toggled.connect(self.toggle_completion)
        header_layout.addWidget(self.completed_cb)
        
        # Task title
        self.title_label = QLabel(self.task.title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        if self.task.status == TaskStatus.DONE:
            self.title_label.setStyleSheet("text-decoration: line-through; color: #888;")
        header_layout.addWidget(self.title_label, 1)
        
        # Priority indicator
        priority_color = {
            TaskPriority.LOW: "#4CAF50",
            TaskPriority.MEDIUM: "#FF9800", 
            TaskPriority.HIGH: "#FF5722",
            TaskPriority.URGENT: "#E91E63"
        }
        
        priority_label = QLabel(self.task.priority.value.upper())
        priority_label.setStyleSheet(f"""
            background-color: {priority_color[self.task.priority]};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        priority_label.setFixedHeight(20)
        header_layout.addWidget(priority_label)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(24, 24)
        edit_btn.clicked.connect(self.edit_task)
        header_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(24, 24)
        delete_btn.clicked.connect(self.delete_task)
        header_layout.addWidget(delete_btn)
        
        layout.addLayout(header_layout)
        
        # Description (if present)
        if self.task.description:
            desc_label = QLabel(self.task.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-size: 10px; margin-left: 20px;")
            layout.addWidget(desc_label)
        
        # Footer with due date and time info
        footer_layout = QHBoxLayout()
        
        if self.task.due_date:
            due_label = QLabel(f"Due: {self.task.due_date.strftime('%Y-%m-%d %H:%M')}")
            due_label.setStyleSheet("color: #666; font-size: 10px;")
            
            # Check if overdue
            if self.task.due_date < datetime.datetime.now() and self.task.status != TaskStatus.DONE:
                due_label.setStyleSheet("color: #f44336; font-size: 10px; font-weight: bold;")
            
            footer_layout.addWidget(due_label)
        
        if self.task.estimated_hours > 0:
            time_label = QLabel(f"Est: {self.task.estimated_hours}h")
            time_label.setStyleSheet("color: #666; font-size: 10px;")
            footer_layout.addWidget(time_label)
        
        if self.task.actual_hours > 0:
            actual_label = QLabel(f"Actual: {self.task.actual_hours:.1f}h")
            actual_label.setStyleSheet("color: #666; font-size: 10px;")
            footer_layout.addWidget(actual_label)
        
        footer_layout.addStretch()
        
        if footer_layout.count() > 1:  # Only add if there are items
            layout.addLayout(footer_layout)
        
        # Styling
        self.setStyleSheet("""
            TaskWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                margin: 2px;
            }
            TaskWidget:hover {
                border-color: #2196F3;
                background-color: #f5f5f5;
            }
        """)
        
    def toggle_completion(self, checked: bool):
        """Toggle task completion status"""
        new_status = TaskStatus.DONE if checked else TaskStatus.TODO
        self.task_manager.update_task(self.task.id, status=new_status)
        self.task_updated.emit(self.task.id)
        
    def edit_task(self):
        """Open task edit dialog"""
        dialog = TaskEditDialog(self.task, self.task_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.task_updated.emit(self.task.id)
            
    def delete_task(self):
        """Delete task with confirmation"""
        reply = QMessageBox.question(self, "Delete Task", 
                                   f"Are you sure you want to delete '{self.task.title}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.task_manager.delete_task(self.task.id)
            self.task_deleted.emit(self.task.id)

class TaskEditDialog(QDialog):
    """Dialog for editing tasks"""
    
    def __init__(self, task: Optional[Task] = None, task_manager: TaskManager = None, parent=None):
        super().__init__(parent)
        self.task = task
        self.task_manager = task_manager
        self.is_new = task is None
        
        if self.is_new:
            self.task = Task(id="", title="", description="")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("Edit Task" if not self.is_new else "New Task")
        self.setMinimumSize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Title
        self.title_edit = QLineEdit(self.task.title)
        form_layout.addRow("Title:", self.title_edit)
        
        # Description
        self.description_edit = QTextEdit(self.task.description)
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        for priority in TaskPriority:
            self.priority_combo.addItem(priority.value.title(), priority)
        
        current_index = list(TaskPriority).index(self.task.priority)
        self.priority_combo.setCurrentIndex(current_index)
        form_layout.addRow("Priority:", self.priority_combo)
        
        # Status
        self.status_combo = QComboBox()
        for status in TaskStatus:
            self.status_combo.addItem(status.value.replace('_', ' ').title(), status)
        
        current_index = list(TaskStatus).index(self.task.status)
        self.status_combo.setCurrentIndex(current_index)
        form_layout.addRow("Status:", self.status_combo)
        
        # Project
        self.project_combo = QComboBox()
        self.project_combo.addItem("No Project", None)
        for project in self.task_manager.projects.values():
            self.project_combo.addItem(project.name, project.id)
        
        if self.task.project_id:
            for i in range(self.project_combo.count()):
                if self.project_combo.itemData(i) == self.task.project_id:
                    self.project_combo.setCurrentIndex(i)
                    break
        
        form_layout.addRow("Project:", self.project_combo)
        
        # Due date
        self.due_date_edit = QDateTimeEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDateTime(QDateTime.currentDateTime())
        
        self.due_date_enabled = QCheckBox("Set due date")
        due_layout = QHBoxLayout()
        due_layout.addWidget(self.due_date_enabled)
        due_layout.addWidget(self.due_date_edit)
        
        if self.task.due_date:
            self.due_date_enabled.setChecked(True)
            self.due_date_edit.setDateTime(QDateTime.fromSecsSinceEpoch(int(self.task.due_date.timestamp())))
        else:
            self.due_date_edit.setEnabled(False)
            
        self.due_date_enabled.toggled.connect(self.due_date_edit.setEnabled)
        
        form_layout.addRow("Due Date:", due_layout)
        
        # Estimated hours
        self.estimated_hours_spin = QSpinBox()
        self.estimated_hours_spin.setRange(0, 999)
        self.estimated_hours_spin.setValue(int(self.task.estimated_hours))
        self.estimated_hours_spin.setSuffix(" hours")
        form_layout.addRow("Estimated Hours:", self.estimated_hours_spin)
        
        # Tags
        self.tags_edit = QLineEdit(", ".join(self.task.tags))
        self.tags_edit.setPlaceholderText("Comma-separated tags")
        form_layout.addRow("Tags:", self.tags_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def accept(self):
        """Accept dialog and save task"""
        # Validate
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Task title is required!")
            return
        
        # Update task data
        self.task.title = self.title_edit.text().strip()
        self.task.description = self.description_edit.toPlainText().strip()
        self.task.priority = self.priority_combo.currentData()
        self.task.status = self.status_combo.currentData()
        self.task.project_id = self.project_combo.currentData()
        self.task.estimated_hours = float(self.estimated_hours_spin.value())
        
        # Due date
        if self.due_date_enabled.isChecked():
            self.task.due_date = self.due_date_edit.dateTime().toPython()
        else:
            self.task.due_date = None
            
        # Tags
        tags_text = self.tags_edit.text().strip()
        if tags_text:
            self.task.tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        else:
            self.task.tags = []
        
        # Save to manager
        if self.is_new:
            self.task_manager.add_task(self.task)
        else:
            self.task_manager.update_task(
                self.task.id,
                title=self.task.title,
                description=self.task.description,
                priority=self.task.priority,
                status=self.task.status,
                project_id=self.task.project_id,
                estimated_hours=self.task.estimated_hours,
                due_date=self.task.due_date,
                tags=self.task.tags
            )
        
        super().accept()

class ProjectWidget(ModernCard):
    """Widget for displaying project information"""
    
    project_selected = pyqtSignal(str)  # project_id
    
    def __init__(self, project: Project, task_manager: TaskManager, parent=None):
        self.project = project
        self.task_manager = task_manager
        super().__init__(project.name, project.description, parent)
        self.setup_project_ui()
        
    def setup_project_ui(self):
        """Setup project-specific UI elements"""
        layout = self.layout()
        
        # Progress bar
        progress = self.task_manager.calculate_project_progress(self.project.id)
        
        progress_layout = QHBoxLayout()
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(progress))
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f0f0f0;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {self.project.color};
                border-radius: 4px;
            }}
        """)
        
        progress_label = QLabel(f"{progress:.1f}%")
        progress_layout.addWidget(progress_bar)
        progress_layout.addWidget(progress_label)
        
        layout.addLayout(progress_layout)
        
        # Task counts
        tasks = self.task_manager.get_tasks_by_project(self.project.id)
        todo_count = len([t for t in tasks if t.status == TaskStatus.TODO])
        in_progress_count = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
        done_count = len([t for t in tasks if t.status == TaskStatus.DONE])
        
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel(f"📝 {todo_count}"))
        stats_layout.addWidget(QLabel(f"🔄 {in_progress_count}"))
        stats_layout.addWidget(QLabel(f"✅ {done_count}"))
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Click to select
        self.mousePressEvent = self.on_click
        
    def on_click(self, event):
        """Handle project click"""
        self.project_selected.emit(self.project.id)

class TaskBoardWidget(QWidget):
    """Kanban-style task board"""
    
    def __init__(self, task_manager: TaskManager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.current_project_id = None
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup task board UI"""
        layout = QVBoxLayout(self)
        
        # Header with project selector
        header_layout = QHBoxLayout()
        
        header_layout.addWidget(QLabel("Project:"))
        
        self.project_combo = QComboBox()
        self.project_combo.addItem("All Tasks", None)
        self.update_project_combo()
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        header_layout.addWidget(self.project_combo)
        
        header_layout.addStretch()
        
        # Add task button
        add_task_btn = ModernButton("+ Add Task")
        add_task_btn.clicked.connect(self.add_task)
        header_layout.addWidget(add_task_btn)
        
        layout.addLayout(header_layout)
        
        # Kanban columns
        columns_layout = QHBoxLayout()
        
        # TODO column
        todo_group = QGroupBox("To Do")
        todo_layout = QVBoxLayout(todo_group)
        self.todo_list = QListWidget()
        self.todo_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        todo_layout.addWidget(self.todo_list)
        columns_layout.addWidget(todo_group)
        
        # In Progress column
        progress_group = QGroupBox("In Progress")
        progress_layout = QVBoxLayout(progress_group)
        self.progress_list = QListWidget()
        self.progress_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        progress_layout.addWidget(self.progress_list)
        columns_layout.addWidget(progress_group)
        
        # Done column
        done_group = QGroupBox("Done")
        done_layout = QVBoxLayout(done_group)
        self.done_list = QListWidget()
        self.done_list.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        done_layout.addWidget(self.done_list)
        columns_layout.addWidget(done_group)
        
        layout.addLayout(columns_layout)
        
        self.update_board()
        
    def connect_signals(self):
        """Connect task manager signals"""
        self.task_manager.tasks_updated.connect(self.update_board)
        self.task_manager.projects_updated.connect(self.update_project_combo)
        
    def update_project_combo(self):
        """Update project combo box"""
        current_data = self.project_combo.currentData()
        self.project_combo.clear()
        self.project_combo.addItem("All Tasks", None)
        
        for project in self.task_manager.projects.values():
            self.project_combo.addItem(project.name, project.id)
        
        # Restore selection
        for i in range(self.project_combo.count()):
            if self.project_combo.itemData(i) == current_data:
                self.project_combo.setCurrentIndex(i)
                break
                
    def on_project_changed(self):
        """Handle project selection change"""
        self.current_project_id = self.project_combo.currentData()
        self.update_board()
        
    def update_board(self):
        """Update task board with current tasks"""
        # Clear lists
        self.todo_list.clear()
        self.progress_list.clear()
        self.done_list.clear()
        
        # Get tasks to display
        if self.current_project_id:
            tasks = self.task_manager.get_tasks_by_project(self.current_project_id)
        else:
            tasks = list(self.task_manager.tasks.values())
        
        # Sort tasks by priority and due date
        tasks.sort(key=lambda t: (
            list(TaskPriority).index(t.priority),
            t.due_date if t.due_date else datetime.datetime.max
        ))
        
        # Add tasks to appropriate columns
        for task in tasks:
            task_widget = TaskWidget(task, self.task_manager)
            task_widget.task_updated.connect(self.update_board)
            task_widget.task_deleted.connect(self.update_board)
            
            item = QListWidgetItem()
            item.setSizeHint(task_widget.sizeHint())
            
            if task.status == TaskStatus.TODO:
                self.todo_list.addItem(item)
                self.todo_list.setItemWidget(item, task_widget)
            elif task.status == TaskStatus.IN_PROGRESS:
                self.progress_list.addItem(item)
                self.progress_list.setItemWidget(item, task_widget)
            elif task.status == TaskStatus.DONE:
                self.done_list.addItem(item)
                self.done_list.setItemWidget(item, task_widget)
                
    def add_task(self):
        """Add new task"""
        dialog = TaskEditDialog(task_manager=self.task_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.update_board()

class TimeTrackerWidget(QWidget):
    """Time tracking widget"""
    
    def __init__(self, task_manager: TaskManager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.active_entry_id = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer_display)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup time tracker UI"""
        layout = QVBoxLayout(self)
        
        # Current tracking section
        current_group = QGroupBox("Current Session")
        current_layout = QVBoxLayout(current_group)
        
        # Task selector
        task_layout = QHBoxLayout()
        task_layout.addWidget(QLabel("Task:"))
        
        self.task_combo = QComboBox()
        self.update_task_combo()
        task_layout.addWidget(self.task_combo)
        
        current_layout.addLayout(task_layout)
        
        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("color: #2196F3; margin: 20px;")
        current_layout.addWidget(self.timer_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_btn = ModernButton("▶ Start")
        self.start_btn.clicked.connect(self.start_tracking)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = ModernButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_tracking)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        current_layout.addLayout(control_layout)
        
        layout.addWidget(current_group)
        
        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("What are you working on?")
        current_layout.addWidget(self.description_edit)
        
        layout.addWidget(current_group)
        layout.addStretch()
        
    def update_task_combo(self):
        """Update task combo with available tasks"""
        self.task_combo.clear()
        
        for task in self.task_manager.tasks.values():
            if task.status != TaskStatus.DONE:
                self.task_combo.addItem(f"{task.title} ({task.priority.value})", task.id)
                
    def start_tracking(self):
        """Start time tracking"""
        if self.task_combo.currentData():
            self.active_entry_id = self.task_manager.start_time_tracking(
                self.task_combo.currentData(),
                self.description_edit.text()
            )
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.task_combo.setEnabled(False)
            
            self.timer.start(1000)  # Update every second
            
    def stop_tracking(self):
        """Stop time tracking"""
        if self.active_entry_id:
            self.task_manager.stop_time_tracking(self.active_entry_id)
            self.active_entry_id = None
            
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.task_combo.setEnabled(True)
        
        self.timer.stop()
        self.timer_label.setText("00:00:00")
        
    def update_timer_display(self):
        """Update timer display"""
        if self.active_entry_id and self.active_entry_id in self.task_manager.time_entries:
            entry = self.task_manager.time_entries[self.active_entry_id]
            elapsed = datetime.datetime.now() - entry.start_time
            
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

class ProductivityDashboard(QWidget):
    """Main productivity dashboard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task_manager = TaskManager()
        self.notification_manager = NotificationManager(self)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dashboard UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Productivity Dashboard")
        header.setFont(QFont("", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("margin: 20px; color: #333;")
        layout.addWidget(header)
        
        # Main content tabs
        self.tabs = QTabWidget()
        
        # Task Board tab
        self.task_board = TaskBoardWidget(self.task_manager)
        self.tabs.addTab(self.task_board, "📋 Task Board")
        
        # Time Tracker tab
        self.time_tracker = TimeTrackerWidget(self.task_manager)
        self.tabs.addTab(self.time_tracker, "⏱️ Time Tracker")
        
        # Projects tab (placeholder for now)
        projects_widget = QWidget()
        projects_layout = QVBoxLayout(projects_widget)
        projects_layout.addWidget(QLabel("Projects management coming soon..."))
        self.tabs.addTab(projects_widget, "📁 Projects")
        
        # Analytics tab (placeholder for now)
        analytics_widget = QWidget()
        analytics_layout = QVBoxLayout(analytics_widget)
        analytics_layout.addWidget(QLabel("Analytics and reports coming soon..."))
        self.tabs.addTab(analytics_widget, "📊 Analytics")
        
        layout.addWidget(self.tabs)
        
        # Add some demo data if no tasks exist
        self.add_demo_data()
        
    def add_demo_data(self):
        """Add demo data if database is empty"""
        if not self.task_manager.tasks and not self.task_manager.projects:
            # Add demo project
            demo_project = Project(
                id="",
                name="Website Redesign",
                description="Complete redesign of company website",
                status=ProjectStatus.ACTIVE,
                color="#4CAF50"
            )
            project_id = self.task_manager.add_project(demo_project)
            
            # Add demo tasks
            demo_tasks = [
                Task(
                    id="",
                    title="Design wireframes",
                    description="Create wireframes for all main pages",
                    priority=TaskPriority.HIGH,
                    status=TaskStatus.IN_PROGRESS,
                    project_id=project_id,
                    estimated_hours=8.0,
                    due_date=datetime.datetime.now() + datetime.timedelta(days=3)
                ),
                Task(
                    id="",
                    title="Setup development environment",
                    description="Configure local development environment with all necessary tools",
                    priority=TaskPriority.MEDIUM,
                    status=TaskStatus.DONE,
                    project_id=project_id,
                    estimated_hours=4.0,
                    actual_hours=3.5
                ),
                Task(
                    id="",
                    title="Research color schemes",
                    description="Research and propose new color schemes for the brand",
                    priority=TaskPriority.LOW,
                    status=TaskStatus.TODO,
                    project_id=project_id,
                    estimated_hours=2.0
                )
            ]
            
            for task in demo_tasks:
                self.task_manager.add_task(task)
                
            self.notification_manager.show_info("Demo data loaded! Start managing your tasks.")
