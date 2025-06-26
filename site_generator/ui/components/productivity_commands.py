"""
Productivity Commands Extension
Extended commands for the Command Palette focused on productivity features.
"""

import os
import subprocess
import datetime
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass

from PyQt6.QtWidgets import QWidget, QDialog, QMessageBox, QInputDialog
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon

from .productivity_tools import TaskManager, Task, Project, TaskPriority, TaskStatus, ProjectStatus

@dataclass
class ProductivityCommand:
    """Extended command structure for productivity features"""
    name: str
    description: str
    category: str
    action: Callable
    icon: str = "⚡"
    shortcut: str = ""
    requires_selection: bool = False
    context_sensitive: bool = False

class ProductivityCommandManager(QObject):
    """Manager for productivity-related commands"""
    
    command_executed = pyqtSignal(str, dict)  # command_name, result
    
    def __init__(self, task_manager: TaskManager, parent=None):
        super().__init__(parent)
        self.task_manager = task_manager
        self.commands = {}
        self.setup_commands()
    
    def setup_commands(self):
        """Setup all productivity commands"""
        
        # Task Management Commands
        task_commands = [
            ProductivityCommand(
                name="Quick Add Task",
                description="Quickly add a new task",
                category="Tasks",
                action=self.quick_add_task,
                icon="✚",
                shortcut="Ctrl+Shift+T"
            ),
            ProductivityCommand(
                name="Mark Task Complete",
                description="Mark selected task as complete",
                category="Tasks", 
                action=self.mark_task_complete,
                icon="✅",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Set Task Priority High",
                description="Set selected task priority to high",
                category="Tasks",
                action=lambda: self.set_task_priority(TaskPriority.HIGH),
                icon="🔴",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Set Task Priority Medium",
                description="Set selected task priority to medium",
                category="Tasks",
                action=lambda: self.set_task_priority(TaskPriority.MEDIUM),
                icon="🟡",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Set Task Priority Low",
                description="Set selected task priority to low",
                category="Tasks",
                action=lambda: self.set_task_priority(TaskPriority.LOW),
                icon="🟢",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Add Task to Project",
                description="Assign selected task to a project",
                category="Tasks",
                action=self.assign_task_to_project,
                icon="📁",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Set Task Due Date",
                description="Set due date for selected task",
                category="Tasks",
                action=self.set_task_due_date,
                icon="📅",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Show Overdue Tasks",
                description="Display all overdue tasks",
                category="Tasks",
                action=self.show_overdue_tasks,
                icon="⏰"
            ),
            ProductivityCommand(
                name="Show Today's Tasks",
                description="Display tasks due today",
                category="Tasks",
                action=self.show_todays_tasks,
                icon="📋"
            ),
            ProductivityCommand(
                name="Archive Completed Tasks",
                description="Archive all completed tasks",
                category="Tasks",
                action=self.archive_completed_tasks,
                icon="📦"
            )
        ]
        
        # Project Management Commands
        project_commands = [
            ProductivityCommand(
                name="New Project",
                description="Create a new project",
                category="Projects",
                action=self.create_new_project,
                icon="📂",
                shortcut="Ctrl+Shift+P"
            ),
            ProductivityCommand(
                name="Project Progress Report",
                description="Generate progress report for selected project",
                category="Projects",
                action=self.generate_project_report,
                icon="📊",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Set Project Status Active",
                description="Set project status to active",
                category="Projects",
                action=lambda: self.set_project_status(ProjectStatus.ACTIVE),
                icon="🟢",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Set Project Status On Hold",
                description="Set project status to on hold",
                category="Projects",
                action=lambda: self.set_project_status(ProjectStatus.ON_HOLD),
                icon="⏸️",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Complete Project",
                description="Mark project as completed",
                category="Projects",
                action=lambda: self.set_project_status(ProjectStatus.COMPLETED),
                icon="✅",
                requires_selection=True
            )
        ]
        
        # Time Management Commands
        time_commands = [
            ProductivityCommand(
                name="Start Pomodoro Timer",
                description="Start a 25-minute focused work session",
                category="Time",
                action=self.start_pomodoro,
                icon="🍅",
                shortcut="Ctrl+Shift+F"
            ),
            ProductivityCommand(
                name="Take Short Break",
                description="Start a 5-minute break timer",
                category="Time",
                action=self.start_short_break,
                icon="☕"
            ),
            ProductivityCommand(
                name="Take Long Break",
                description="Start a 15-minute break timer",
                category="Time",
                action=self.start_long_break,
                icon="🛋️"
            ),
            ProductivityCommand(
                name="Track Time for Task",
                description="Start time tracking for selected task",
                category="Time",
                action=self.track_task_time,
                icon="⏱️",
                requires_selection=True
            ),
            ProductivityCommand(
                name="Stop Time Tracking",
                description="Stop current time tracking session",
                category="Time",
                action=self.stop_time_tracking,
                icon="⏹️"
            ),
            ProductivityCommand(
                name="Today's Time Report",
                description="Show time tracking report for today",
                category="Time",
                action=self.show_daily_time_report,
                icon="📈"
            )
        ]
        
        # Workflow Commands
        workflow_commands = [
            ProductivityCommand(
                name="Daily Standup",
                description="Quick review of yesterday's work and today's plan",
                category="Workflow",
                action=self.daily_standup,
                icon="🌅"
            ),
            ProductivityCommand(
                name="Weekly Review",
                description="Review weekly progress and plan ahead",
                category="Workflow",
                action=self.weekly_review,
                icon="📝"
            ),
            ProductivityCommand(
                name="Focus Mode",
                description="Enable distraction-free focus mode",
                category="Workflow",
                action=self.enable_focus_mode,
                icon="🎯"
            ),
            ProductivityCommand(
                name="Brain Dump",
                description="Quickly capture all thoughts and ideas",
                category="Workflow",
                action=self.brain_dump,
                icon="🧠"
            ),
            ProductivityCommand(
                name="Energy Check",
                description="Quick energy level assessment and suggestions",
                category="Workflow",
                action=self.energy_check,
                icon="⚡"
            )
        ]
        
        # Analytics Commands
        analytics_commands = [
            ProductivityCommand(
                name="Productivity Analytics",
                description="View detailed productivity analytics",
                category="Analytics",
                action=self.show_productivity_analytics,
                icon="📊"
            ),
            ProductivityCommand(
                name="Task Completion Trends",
                description="Show task completion trends over time",
                category="Analytics",
                action=self.show_completion_trends,
                icon="📈"
            ),
            ProductivityCommand(
                name="Time Distribution",
                description="Show how time is distributed across projects",
                category="Analytics",
                action=self.show_time_distribution,
                icon="🥧"
            ),
            ProductivityCommand(
                name="Export Data",
                description="Export productivity data to CSV",
                category="Analytics",
                action=self.export_productivity_data,
                icon="💾"
            )
        ]
        
        # Integration Commands
        integration_commands = [
            ProductivityCommand(
                name="Sync with Calendar",
                description="Sync tasks with external calendar",
                category="Integration",
                action=self.sync_with_calendar,
                icon="📅"
            ),
            ProductivityCommand(
                name="Email Weekly Report",
                description="Email weekly productivity report",
                category="Integration",
                action=self.email_weekly_report,
                icon="📧"
            ),
            ProductivityCommand(
                name="Backup Data",
                description="Create backup of all productivity data",
                category="Integration",
                action=self.backup_data,
                icon="💾"
            ),
            ProductivityCommand(
                name="Import Tasks from File",
                description="Import tasks from CSV or JSON file",
                category="Integration",
                action=self.import_tasks,
                icon="📥"
            )
        ]
        
        # Combine all commands
        all_commands = (task_commands + project_commands + time_commands + 
                       workflow_commands + analytics_commands + integration_commands)
        
        # Register commands
        for cmd in all_commands:
            self.commands[cmd.name] = cmd
    
    def get_commands(self) -> Dict[str, ProductivityCommand]:
        """Get all available commands"""
        return self.commands
    
    def get_commands_by_category(self, category: str) -> List[ProductivityCommand]:
        """Get commands by category"""
        return [cmd for cmd in self.commands.values() if cmd.category == category]
    
    def execute_command(self, command_name: str, context: Dict[str, Any] = None):
        """Execute a command by name"""
        if command_name in self.commands:
            cmd = self.commands[command_name]
            try:
                if context is None:
                    context = {}
                result = cmd.action()
                self.command_executed.emit(command_name, {"success": True, "result": result})
                return result
            except Exception as e:
                self.command_executed.emit(command_name, {"success": False, "error": str(e)})
                raise e
        else:
            raise ValueError(f"Command '{command_name}' not found")
    
    # Task Management Actions
    def quick_add_task(self):
        """Quick add task dialog"""
        from PyQt6.QtWidgets import QInputDialog
        
        title, ok = QInputDialog.getText(None, "Quick Add Task", "Task title:")
        if ok and title.strip():
            task = Task(
                id="",
                title=title.strip(),
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.TODO
            )
            task_id = self.task_manager.add_task(task)
            return {"task_id": task_id, "message": f"Task '{title}' created successfully"}
        return {"message": "Task creation cancelled"}
    
    def mark_task_complete(self, task_id: str = None):
        """Mark task as complete"""
        if not task_id:
            # Get from current selection or prompt
            task_id = self._get_selected_task_id()
            
        if task_id and task_id in self.task_manager.tasks:
            self.task_manager.update_task(task_id, status=TaskStatus.DONE)
            task = self.task_manager.tasks[task_id]
            return {"message": f"Task '{task.title}' marked as complete"}
        return {"error": "No task selected or task not found"}
    
    def set_task_priority(self, priority: TaskPriority, task_id: str = None):
        """Set task priority"""
        if not task_id:
            task_id = self._get_selected_task_id()
            
        if task_id and task_id in self.task_manager.tasks:
            self.task_manager.update_task(task_id, priority=priority)
            task = self.task_manager.tasks[task_id]
            return {"message": f"Task '{task.title}' priority set to {priority.value}"}
        return {"error": "No task selected or task not found"}
    
    def assign_task_to_project(self, task_id: str = None):
        """Assign task to project"""
        if not task_id:
            task_id = self._get_selected_task_id()
            
        if task_id and task_id in self.task_manager.tasks:
            # Show project selection dialog
            projects = list(self.task_manager.projects.values())
            if not projects:
                return {"error": "No projects available"}
                
            from PyQt6.QtWidgets import QInputDialog
            project_names = [p.name for p in projects]
            project_name, ok = QInputDialog.getItem(
                None, "Select Project", "Choose project:", project_names, 0, False
            )
            
            if ok:
                project = next(p for p in projects if p.name == project_name)
                self.task_manager.update_task(task_id, project_id=project.id)
                task = self.task_manager.tasks[task_id]
                return {"message": f"Task '{task.title}' assigned to project '{project.name}'"}
        return {"error": "No task selected or operation cancelled"}
    
    def set_task_due_date(self, task_id: str = None):
        """Set task due date"""
        if not task_id:
            task_id = self._get_selected_task_id()
            
        if task_id and task_id in self.task_manager.tasks:
            from PyQt6.QtWidgets import QInputDialog
            from PyQt6.QtCore import QDate
            
            # Simple date input (could be enhanced with date picker)
            date_str, ok = QInputDialog.getText(
                None, "Set Due Date", 
                "Enter due date (YYYY-MM-DD) or days from now (e.g., '+3'):"
            )
            
            if ok and date_str.strip():
                try:
                    if date_str.startswith('+'):
                        days = int(date_str[1:])
                        due_date = datetime.datetime.now() + datetime.timedelta(days=days)
                    else:
                        due_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    
                    self.task_manager.update_task(task_id, due_date=due_date)
                    task = self.task_manager.tasks[task_id]
                    return {"message": f"Due date set for task '{task.title}'"}
                except ValueError:
                    return {"error": "Invalid date format"}
        return {"error": "No task selected or operation cancelled"}
    
    def show_overdue_tasks(self):
        """Show overdue tasks"""
        overdue = self.task_manager.get_overdue_tasks()
        if overdue:
            tasks_info = [f"• {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})" 
                         for task in overdue]
            message = f"Overdue Tasks ({len(overdue)}):\n\n" + "\n".join(tasks_info)
            QMessageBox.warning(None, "Overdue Tasks", message)
            return {"overdue_count": len(overdue)}
        else:
            QMessageBox.information(None, "Overdue Tasks", "No overdue tasks! 🎉")
            return {"overdue_count": 0}
    
    def show_todays_tasks(self):
        """Show tasks due today"""
        today = datetime.datetime.now().date()
        today_tasks = [task for task in self.task_manager.tasks.values() 
                      if task.due_date and task.due_date.date() == today]
        
        if today_tasks:
            tasks_info = [f"• {task.title} ({task.priority.value})" for task in today_tasks]
            message = f"Tasks Due Today ({len(today_tasks)}):\n\n" + "\n".join(tasks_info)
            QMessageBox.information(None, "Today's Tasks", message)
        else:
            QMessageBox.information(None, "Today's Tasks", "No tasks due today!")
        return {"todays_tasks": len(today_tasks)}
    
    def archive_completed_tasks(self):
        """Archive completed tasks"""
        completed = self.task_manager.get_tasks_by_status(TaskStatus.DONE)
        
        if not completed:
            QMessageBox.information(None, "Archive", "No completed tasks to archive.")
            return {"archived_count": 0}
        
        reply = QMessageBox.question(
            None, "Archive Completed Tasks",
            f"Archive {len(completed)} completed tasks?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # In a real implementation, you might move these to an archive
            # For now, we'll just mark them as archived or delete them
            for task in completed:
                self.task_manager.delete_task(task.id)
            
            QMessageBox.information(None, "Archive", f"Archived {len(completed)} completed tasks.")
            return {"archived_count": len(completed)}
        return {"archived_count": 0}
    
    # Project Management Actions
    def create_new_project(self):
        """Create new project"""
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(None, "New Project", "Project name:")
        if ok and name.strip():
            description, ok2 = QInputDialog.getText(None, "New Project", "Project description (optional):")
            
            project = Project(
                id="",
                name=name.strip(),
                description=description.strip() if ok2 else "",
                status=ProjectStatus.PLANNING
            )
            project_id = self.task_manager.add_project(project)
            return {"project_id": project_id, "message": f"Project '{name}' created successfully"}
        return {"message": "Project creation cancelled"}
    
    def generate_project_report(self, project_id: str = None):
        """Generate project progress report"""
        if not project_id:
            project_id = self._get_selected_project_id()
        
        if project_id and project_id in self.task_manager.projects:
            project = self.task_manager.projects[project_id]
            tasks = self.task_manager.get_tasks_by_project(project_id)
            progress = self.task_manager.calculate_project_progress(project_id)
            
            todo_count = len([t for t in tasks if t.status == TaskStatus.TODO])
            in_progress_count = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
            done_count = len([t for t in tasks if t.status == TaskStatus.DONE])
            
            report = f"""Project Report: {project.name}
            
Status: {project.status.value}
Progress: {progress:.1f}%

Task Breakdown:
• To Do: {todo_count}
• In Progress: {in_progress_count}  
• Done: {done_count}
• Total: {len(tasks)}

Description: {project.description}"""
            
            QMessageBox.information(None, "Project Report", report)
            return {"progress": progress, "task_counts": {
                "todo": todo_count, "in_progress": in_progress_count, "done": done_count
            }}
        return {"error": "No project selected or project not found"}
    
    def set_project_status(self, status: ProjectStatus, project_id: str = None):
        """Set project status"""
        if not project_id:
            project_id = self._get_selected_project_id()
            
        if project_id and project_id in self.task_manager.projects:
            self.task_manager.update_project(project_id, status=status)
            project = self.task_manager.projects[project_id]
            return {"message": f"Project '{project.name}' status set to {status.value}"}
        return {"error": "No project selected or project not found"}
    
    # Time Management Actions
    def start_pomodoro(self):
        """Start pomodoro timer (25 minutes)"""
        return self._start_timer(25 * 60, "Pomodoro Session", "🍅")
    
    def start_short_break(self):
        """Start short break timer (5 minutes)"""
        return self._start_timer(5 * 60, "Short Break", "☕")
    
    def start_long_break(self):
        """Start long break timer (15 minutes)"""
        return self._start_timer(15 * 60, "Long Break", "🛋️")
    
    def _start_timer(self, seconds: int, title: str, icon: str):
        """Start a timer with notification"""
        # This would integrate with a timer widget or notification system
        QMessageBox.information(None, "Timer Started", f"{icon} {title} started ({seconds//60} minutes)")
        return {"timer_duration": seconds, "timer_type": title}
    
    def track_task_time(self, task_id: str = None):
        """Start time tracking for task"""
        if not task_id:
            task_id = self._get_selected_task_id()
            
        if task_id and task_id in self.task_manager.tasks:
            entry_id = self.task_manager.start_time_tracking(task_id)
            task = self.task_manager.tasks[task_id]
            return {"entry_id": entry_id, "message": f"Time tracking started for '{task.title}'"}
        return {"error": "No task selected or task not found"}
    
    def stop_time_tracking(self):
        """Stop current time tracking"""
        # Find active time entries
        active_entries = [entry for entry in self.task_manager.time_entries.values() 
                         if entry.is_running]
        
        if active_entries:
            for entry in active_entries:
                self.task_manager.stop_time_tracking(entry.id)
            return {"message": f"Stopped {len(active_entries)} time tracking session(s)"}
        return {"message": "No active time tracking sessions"}
    
    def show_daily_time_report(self):
        """Show today's time tracking report"""
        today = datetime.datetime.now().date()
        today_entries = [entry for entry in self.task_manager.time_entries.values()
                        if entry.start_time.date() == today and entry.end_time]
        
        if today_entries:
            total_time = sum((entry.end_time - entry.start_time).total_seconds() 
                           for entry in today_entries) / 3600
            
            report = f"Today's Time Report\n\nTotal time tracked: {total_time:.1f} hours\n\nSessions: {len(today_entries)}"
            QMessageBox.information(None, "Daily Time Report", report)
            return {"total_hours": total_time, "sessions": len(today_entries)}
        else:
            QMessageBox.information(None, "Daily Time Report", "No time tracked today.")
            return {"total_hours": 0, "sessions": 0}
    
    # Workflow Actions  
    def daily_standup(self):
        """Daily standup review"""
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        yesterday_tasks = [task for task in self.task_manager.tasks.values()
                          if (task.completed_at and task.completed_at.date() == yesterday.date()) or
                             (task.updated_at and task.updated_at.date() == yesterday.date())]
        
        today_tasks = [task for task in self.task_manager.tasks.values()
                      if task.due_date and task.due_date.date() == datetime.datetime.now().date()]
        
        standup = f"""Daily Standup
        
Yesterday's Progress:
• {len(yesterday_tasks)} tasks worked on

Today's Plan:
• {len(today_tasks)} tasks due today

Blockers:
• Review overdue tasks for potential blockers"""

        QMessageBox.information(None, "Daily Standup", standup)
        return {"yesterday_tasks": len(yesterday_tasks), "today_tasks": len(today_tasks)}
    
    def weekly_review(self):
        """Weekly review process"""
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        week_tasks = [task for task in self.task_manager.tasks.values()
                     if task.completed_at and task.completed_at >= week_ago]
        
        review = f"""Weekly Review
        
This Week's Accomplishments:
• {len(week_tasks)} tasks completed
• Progress made on {len(set(task.project_id for task in week_tasks if task.project_id))} projects

Next Week's Focus:
• Review upcoming due dates
• Plan high-priority tasks"""

        QMessageBox.information(None, "Weekly Review", review)
        return {"completed_tasks": len(week_tasks)}
    
    def enable_focus_mode(self):
        """Enable focus mode"""
        QMessageBox.information(None, "Focus Mode", "🎯 Focus Mode Enabled\n\nDistractions minimized for deep work.")
        return {"message": "Focus mode enabled"}
    
    def brain_dump(self):
        """Quick brain dump for capturing ideas"""
        from PyQt6.QtWidgets import QInputDialog
        
        ideas, ok = QInputDialog.getMultiLineText(
            None, "Brain Dump", 
            "Capture all your thoughts, ideas, and tasks:\n(One per line)"
        )
        
        if ok and ideas.strip():
            lines = [line.strip() for line in ideas.split('\n') if line.strip()]
            
            # Create tasks from brain dump
            created_tasks = []
            for line in lines:
                if len(line) > 3:  # Only create tasks for substantial entries
                    task = Task(
                        id="",
                        title=line,
                        priority=TaskPriority.MEDIUM,
                        status=TaskStatus.TODO
                    )
                    task_id = self.task_manager.add_task(task)
                    created_tasks.append(task_id)
            
            return {"message": f"Created {len(created_tasks)} tasks from brain dump", 
                   "task_ids": created_tasks}
        return {"message": "Brain dump cancelled"}
    
    def energy_check(self):
        """Check energy level and provide suggestions"""
        from PyQt6.QtWidgets import QInputDialog
        
        energy_levels = ["Very Low", "Low", "Medium", "High", "Very High"]
        energy, ok = QInputDialog.getItem(
            None, "Energy Check", "How's your energy level?", energy_levels, 2, False
        )
        
        if ok:
            suggestions = {
                "Very Low": "Consider taking a break, hydrating, or tackling simple tasks.",
                "Low": "Focus on routine tasks or take a short walk.",
                "Medium": "Good time for moderate complexity tasks.",
                "High": "Great time for challenging or creative work!",
                "Very High": "Perfect for your most important and difficult tasks!"
            }
            
            QMessageBox.information(
                None, "Energy Check", 
                f"Energy Level: {energy}\n\nSuggestion: {suggestions.get(energy, '')}"
            )
            return {"energy_level": energy, "suggestion": suggestions.get(energy, "")}
        return {"message": "Energy check cancelled"}
    
    # Analytics Actions
    def show_productivity_analytics(self):
        """Show productivity analytics"""
        total_tasks = len(self.task_manager.tasks)
        completed_tasks = len(self.task_manager.get_tasks_by_status(TaskStatus.DONE))
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        analytics = f"""Productivity Analytics
        
Overall Stats:
• Total Tasks: {total_tasks}
• Completed: {completed_tasks} 
• Completion Rate: {completion_rate:.1f}%
• Active Projects: {len([p for p in self.task_manager.projects.values() 
                        if p.status == ProjectStatus.ACTIVE])}"""

        QMessageBox.information(None, "Productivity Analytics", analytics)
        return {"total_tasks": total_tasks, "completed_tasks": completed_tasks, 
                "completion_rate": completion_rate}
    
    def show_completion_trends(self):
        """Show task completion trends"""
        # Simple trend analysis
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)
        recent_completions = [task for task in self.task_manager.tasks.values()
                            if task.completed_at and task.completed_at >= last_week]
        
        QMessageBox.information(
            None, "Completion Trends", 
            f"Tasks completed in last 7 days: {len(recent_completions)}"
        )
        return {"recent_completions": len(recent_completions)}
    
    def show_time_distribution(self):
        """Show time distribution across projects"""
        # Calculate time per project
        project_times = {}
        for entry in self.task_manager.time_entries.values():
            if entry.end_time and entry.task_id in self.task_manager.tasks:
                task = self.task_manager.tasks[entry.task_id]
                if task.project_id:
                    project = self.task_manager.projects.get(task.project_id)
                    if project:
                        duration = (entry.end_time - entry.start_time).total_seconds() / 3600
                        project_times[project.name] = project_times.get(project.name, 0) + duration
        
        if project_times:
            time_info = [f"• {name}: {hours:.1f}h" for name, hours in project_times.items()]
            message = "Time Distribution by Project:\n\n" + "\n".join(time_info)
        else:
            message = "No time tracking data available."
            
        QMessageBox.information(None, "Time Distribution", message)
        return {"project_times": project_times}
    
    def export_productivity_data(self):
        """Export productivity data"""
        try:
            # Create a simple CSV export
            import csv
            filename = f"productivity_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Type', 'ID', 'Title', 'Status', 'Priority', 'Created', 'Due Date'])
                
                for task in self.task_manager.tasks.values():
                    writer.writerow([
                        'Task', task.id, task.title, task.status.value, task.priority.value,
                        task.created_at.isoformat() if task.created_at else '',
                        task.due_date.isoformat() if task.due_date else ''
                    ])
            
            QMessageBox.information(None, "Export Complete", f"Data exported to {filename}")
            return {"filename": filename, "message": "Export successful"}
        except Exception as e:
            QMessageBox.warning(None, "Export Error", f"Failed to export data: {str(e)}")
            return {"error": str(e)}
    
    # Integration Actions
    def sync_with_calendar(self):
        """Sync with external calendar"""
        QMessageBox.information(None, "Calendar Sync", "Calendar sync feature coming soon!")
        return {"message": "Calendar sync not yet implemented"}
    
    def email_weekly_report(self):
        """Email weekly report"""
        QMessageBox.information(None, "Email Report", "Email reporting feature coming soon!")
        return {"message": "Email reporting not yet implemented"}
    
    def backup_data(self):
        """Backup productivity data"""
        try:
            backup_filename = f"productivity_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Copy the current data file
            import shutil
            if os.path.exists(self.task_manager.data_file):
                shutil.copy2(self.task_manager.data_file, backup_filename)
                QMessageBox.information(None, "Backup Complete", f"Data backed up to {backup_filename}")
                return {"filename": backup_filename, "message": "Backup successful"}
            else:
                QMessageBox.warning(None, "Backup Error", "No data file found to backup")
                return {"error": "No data file found"}
        except Exception as e:
            QMessageBox.warning(None, "Backup Error", f"Failed to backup data: {str(e)}")
            return {"error": str(e)}
    
    def import_tasks(self):
        """Import tasks from file"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getOpenFileName(
            None, "Import Tasks", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if filename:
            try:
                if filename.endswith('.csv'):
                    return self._import_csv_tasks(filename)
                elif filename.endswith('.json'):
                    return self._import_json_tasks(filename)
                else:
                    return {"error": "Unsupported file format"}
            except Exception as e:
                QMessageBox.warning(None, "Import Error", f"Failed to import tasks: {str(e)}")
                return {"error": str(e)}
        return {"message": "Import cancelled"}
    
    def _import_csv_tasks(self, filename: str):
        """Import tasks from CSV file"""
        import csv
        imported = 0
        
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'Title' in row and row['Title'].strip():
                    task = Task(
                        id="",
                        title=row['Title'].strip(),
                        description=row.get('Description', '').strip(),
                        priority=TaskPriority(row.get('Priority', 'medium').lower()),
                        status=TaskStatus(row.get('Status', 'todo').lower())
                    )
                    self.task_manager.add_task(task)
                    imported += 1
        
        QMessageBox.information(None, "Import Complete", f"Imported {imported} tasks from CSV")
        return {"imported_count": imported, "message": "CSV import successful"}
    
    def _import_json_tasks(self, filename: str):
        """Import tasks from JSON file"""
        import json
        imported = 0
        
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            
            if 'tasks' in data:
                for task_data in data['tasks']:
                    if isinstance(task_data, dict) and 'title' in task_data:
                        task = Task(
                            id="",
                            title=task_data['title'],
                            description=task_data.get('description', ''),
                            priority=TaskPriority(task_data.get('priority', 'medium')),
                            status=TaskStatus(task_data.get('status', 'todo'))
                        )
                        self.task_manager.add_task(task)
                        imported += 1
        
        QMessageBox.information(None, "Import Complete", f"Imported {imported} tasks from JSON")
        return {"imported_count": imported, "message": "JSON import successful"}
    
    # Helper methods
    def _get_selected_task_id(self) -> Optional[str]:
        """Get currently selected task ID (placeholder - would integrate with UI)"""
        # In a real implementation, this would get the selected task from the UI
        tasks = list(self.task_manager.tasks.keys())
        return tasks[0] if tasks else None
    
    def _get_selected_project_id(self) -> Optional[str]:
        """Get currently selected project ID (placeholder - would integrate with UI)"""
        # In a real implementation, this would get the selected project from the UI
        projects = list(self.task_manager.projects.keys())
        return projects[0] if projects else None

def get_productivity_commands(task_manager: TaskManager) -> ProductivityCommandManager:
    """Factory function to create productivity command manager"""
    return ProductivityCommandManager(task_manager)
