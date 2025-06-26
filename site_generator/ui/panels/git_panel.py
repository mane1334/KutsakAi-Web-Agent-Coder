import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
    QPushButton, QTextEdit, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class GitPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_path = None
        self.setup_ui()
        self.connect_signals()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_git_status)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('🔧 Git Status')
        title.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6e6e6; margin-bottom: 4px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.update_git_btn = QPushButton('🔄 Refresh')
        self.update_git_btn.setStyleSheet("""
            QPushButton {
                background: #10a37f;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0d8a6c;
            }
            QPushButton:pressed {
                background: #0a6b4f;
            }
        """)
        header_layout.addWidget(self.update_git_btn)
        layout.addLayout(header_layout)
        
        # Git status display
        self.git_status = QTextEdit()
        self.git_status.setMaximumHeight(150)
        self.git_status.setReadOnly(True)
        self.git_status.setStyleSheet("""
            QTextEdit {
                background: #1a1a1a;
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.git_status)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.init_git_btn = QPushButton('📁 Init Repo')
        self.commit_btn = QPushButton('💾 Quick Commit')
        self.push_btn = QPushButton('⬆️ Push')
        
        for btn in [self.init_git_btn, self.commit_btn, self.push_btn]:
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
                QPushButton:disabled {
                    background: #1a1a1a;
                    color: #666666;
                    border-color: #2a2a2a;
                }
            """)
        
        actions_layout.addWidget(self.init_git_btn)
        actions_layout.addWidget(self.commit_btn)
        actions_layout.addWidget(self.push_btn)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Initial status
        self.update_git_status()
    
    def connect_signals(self):
        self.update_git_btn.clicked.connect(self.update_git_status)
        self.init_git_btn.clicked.connect(self.init_git_repo)
        self.commit_btn.clicked.connect(self.quick_commit)
        self.push_btn.clicked.connect(self.git_push)
    
    def set_project_path(self, path):
        """Set the project path for Git operations."""
        self.project_path = path
        self.update_git_status()
    
    def run_git_command(self, command):
        """Run a git command and return the output."""
        if not self.project_path:
            return "No project path set"
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_path,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr.strip()}"
        except Exception as e:
            return f"Exception: {str(e)}"
    
    def update_git_status(self):
        """Update the Git status display."""
        if not self.project_path:
            self.git_status.setPlainText("No project loaded")
            self.disable_git_buttons()
            return
        
        # Check if it's a git repository
        git_dir = os.path.join(self.project_path, '.git')
        if not os.path.exists(git_dir):
            self.git_status.setPlainText("Not a Git repository\nClick 'Init Repo' to initialize")
            self.init_git_btn.setEnabled(True)
            self.commit_btn.setEnabled(False)
            self.push_btn.setEnabled(False)
            return
        
        # Get git status
        status_output = self.run_git_command("git status --porcelain")
        branch_output = self.run_git_command("git branch --show-current")
        
        status_text = f"Branch: {branch_output}\n\n"
        
        if status_output:
            status_text += "Changes:\n"
            for line in status_output.split('\n'):
                if line.strip():
                    status_code = line[:2]
                    filename = line[3:]
                    if status_code == ' M':
                        status_text += f"🔴 Modified: {filename}\n"
                    elif status_code == '??':
                        status_text += f"🔵 Untracked: {filename}\n"
                    elif status_code == 'A ':
                        status_text += f"🟢 Added: {filename}\n"
                    elif status_code == 'D ':
                        status_text += f"🟡 Deleted: {filename}\n"
                    else:
                        status_text += f"📄 {status_code}: {filename}\n"
        else:
            status_text += "✅ Working tree clean"
        
        self.git_status.setPlainText(status_text)
        
        # Enable/disable buttons based on status
        self.init_git_btn.setEnabled(False)
        self.commit_btn.setEnabled(bool(status_output))
        self.push_btn.setEnabled(True)
    
    def disable_git_buttons(self):
        """Disable all Git action buttons."""
        self.init_git_btn.setEnabled(False)
        self.commit_btn.setEnabled(False)
        self.push_btn.setEnabled(False)
    
    def init_git_repo(self):
        """Initialize a new Git repository."""
        if not self.project_path:
            QMessageBox.warning(self, "Warning", "No project path set")
            return
        
        result = self.run_git_command("git init")
        if "Initialized" in result or "already exists" in result:
            QMessageBox.information(self, "Success", "Git repository initialized!")
            self.update_git_status()
        else:
            QMessageBox.critical(self, "Error", f"Failed to initialize Git repo:\n{result}")
    
    def quick_commit(self):
        """Perform a quick commit with all changes."""
        if not self.project_path:
            return
        
        # Add all files
        add_result = self.run_git_command("git add .")
        
        # Commit with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-commit: {timestamp}"
        
        commit_result = self.run_git_command(f'git commit -m "{commit_msg}"')
        
        if "nothing to commit" in commit_result:
            QMessageBox.information(self, "Info", "Nothing to commit, working tree clean")
        elif "files changed" in commit_result or "file changed" in commit_result:
            QMessageBox.information(self, "Success", "Changes committed successfully!")
        else:
            QMessageBox.warning(self, "Warning", f"Commit result:\n{commit_result}")
        
        self.update_git_status()
    
    def git_push(self):
        """Push changes to remote repository."""
        if not self.project_path:
            return
        
        push_result = self.run_git_command("git push")
        
        if "Everything up-to-date" in push_result:
            QMessageBox.information(self, "Info", "Everything up-to-date")
        elif "error" in push_result.lower() or "fatal" in push_result.lower():
            QMessageBox.critical(self, "Error", f"Push failed:\n{push_result}")
        else:
            QMessageBox.information(self, "Success", "Changes pushed successfully!")
        
        self.update_git_status()
