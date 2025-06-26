from ollama_client import generate_code
from llm_workers import CodeImproveWorker
from collections import defaultdict
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
import json
import os
from datetime import datetime

class EditorController(QObject):
    # Signals for streaming support
    token_received = pyqtSignal(str, str)  # file_path, token
    improvement_finished = pyqtSignal(str, str)  # file_path, full_code
    improvement_error = pyqtSignal(str, str)  # file_path, error_message
    improvement_started = pyqtSignal(str)  # file_path
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.system_prompt = ''
        self.doc_keywords = {}
        self.history = defaultdict(list)  # History of improvements
        self.workers = set()  # Storing workers for lifetime management
        self.load_history()  # Load existing history

    def load_project(self, path):
        # Here you would load project specific settings, etc.
        # For now, just update the view
        pass

    def load_history(self):
        """Load existing history from .kutsakai/history.json."""
        try:
            history_path = os.path.join('.kutsakai', 'history.json')
            if os.path.exists(history_path):
                with open(history_path, 'r') as history_file:
                    loaded_history = json.load(history_file)
                    # Convert to defaultdict
                    for file_path, entries in loaded_history.items():
                        self.history[file_path] = entries
        except Exception as e:
            print(f"Error loading history: {e}")

    def start_improvement(self, prompt, code, model, file_path):
        """Start async improvement with streaming support"""
        worker = CodeImproveWorker(prompt, code, model, file_path)
        self.workers.add(worker)
        
        # Connect worker signals
        worker.started.connect(lambda: self.improvement_started.emit(file_path))
        worker.token.connect(lambda text: self.on_token(file_path, text))
        worker.finished.connect(lambda full_code: self.on_finished(file_path, full_code, {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'model': model,
            'auto_save': self.view.auto_save_enabled() if hasattr(self.view, 'auto_save_enabled') else False
        }))
        worker.error.connect(lambda msg: self.on_error(file_path, msg))
        
        # Clean up worker when finished
        worker.finished.connect(lambda: self.workers.discard(worker))
        worker.error.connect(lambda: self.workers.discard(worker))
        
        worker.start()

    def improve_code(self, prompt, code, model):
        # Call the actual AI model here
        full_prompt = f"""
        You are an AI assistant specialized in improving code.
        Improve the following code based on the user's prompt.
        Only return the improved code, do not add any extra text or explanations.

        User's prompt: {prompt}

        Code to improve:
        {code}
        """
        improved_code = generate_code(full_prompt, model=model)
        return improved_code

    def edit_system_prompt(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        dialog = QDialog(self.view)
        dialog.setWindowTitle('Edit System Prompt')
        layout = QVBoxLayout(dialog)
        editor = QTextEdit()
        editor.setPlainText(self.system_prompt)
        layout.addWidget(editor)
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(lambda: self.save_system_prompt(editor.toPlainText(), dialog))
        layout.addWidget(save_btn)
        dialog.exec()

    def on_token(self, file_path, text):
        """Handle token received from streaming worker"""
        # Emit signal for view to handle streaming display
        self.token_received.emit(file_path, text)

    def on_finished(self, file_path, full_code, meta):
        """Handle improvement completion"""
        # Update history
        history_entry = {
            'ts': meta['timestamp'],
            'code': full_code,
            'prompt': meta['prompt'],
            'model': meta['model']
        }
        self.history[file_path].append(history_entry)

        # Persist to .kutsakai/history.json
        try:
            history_path = os.path.join('.kutsakai', 'history.json')
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            with open(history_path, 'w') as history_file:
                # Convert defaultdict to regular dict for JSON serialization
                json.dump(dict(self.history), history_file, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

        # Emit signal for view to handle completion
        self.improvement_finished.emit(file_path, full_code)

    def on_error(self, file_path, msg):
        """Handle improvement error"""
        # Try to restore backup if available
        if file_path:
            backup_restored = self.restore_backup(file_path)
            if backup_restored:
                msg += "\n\nBackup has been restored."
        
        # Emit signal for view to handle error
        self.improvement_error.emit(file_path, msg)

    def restore_backup(self, file_path):
        """Restore the most recent backup for a file."""
        try:
            backup_dir = os.path.join(os.path.dirname(file_path), ".backup")
            if not os.path.exists(backup_dir):
                return False
            
            # Find the most recent backup
            backup_dirs = [d for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))]
            if not backup_dirs:
                return False
            
            latest_backup_dir = max(backup_dirs)
            filename = os.path.basename(file_path)
            backup_file = os.path.join(backup_dir, latest_backup_dir, filename)
            
            if os.path.exists(backup_file):
                import shutil
                shutil.copy2(backup_file, file_path)
                return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
        return False

    def get_file_history(self, file_path):
        """Get the history entries for a specific file."""
        return self.history.get(file_path, [])

    def cleanup_workers(self):
        """Stop and clean up all running workers."""
        for worker in list(self.workers):
            if worker.isRunning():
                worker.requestInterruption()
                worker.wait(5000)  # Wait up to 5 seconds
        self.workers.clear()

    def save_system_prompt(self, text, dialog):
        self.system_prompt = text
        dialog.accept()
