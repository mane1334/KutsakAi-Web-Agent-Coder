import requests
import os
import shutil
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor
from ollama_client import generate_code, generate_code_stream

class LLMWorker(QThread):
    progress = pyqtSignal(int)
    partial = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__()
        self.prompt = kwargs.get('prompt')
        self.model = kwargs.get('model')
        self.stream = kwargs.get('stream', False)
        self.session = requests.Session()
        self._is_cancelled = False
        self.worker_id = kwargs.get('worker_id', 'worker')

    def run(self):
        try:
            if self._is_cancelled:
                self.cancelled.emit()
                return
            
            # Generate code using ollama_client
            def on_progress(progress):
                if not self._is_cancelled:
                    self.progress.emit(progress)
            
            def on_chunk(chunk):
                if not self._is_cancelled:
                    self.partial.emit(chunk)
            
            response = generate_code(
                self.prompt,
                model=self.model,
                session=self.session,
                on_progress=on_progress,
                on_chunk=on_chunk
            )
            
            if self._is_cancelled:
                self.cancelled.emit()
                return
                
            self.finished.emit(response)
            
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))

    def cancel(self):
        self._is_cancelled = True
        self.requestInterruption()


class LLMStreamWorker(LLMWorker):
    def run(self):
        try:
            if self._is_cancelled:
                self.cancelled.emit()
                return
            
            # Utilize generate_code com stream=True
            def on_progress(progress):
                if not self._is_cancelled:
                    self.progress.emit(progress)

            def on_chunk(chunk):
                if not self._is_cancelled:
                    self.partial.emit(chunk)

            # Chamar a função de geração de código com streaming
            response = generate_code(
                self.prompt,
                model=self.model,
                session=self.session,
                on_progress=on_progress,
                on_chunk=on_chunk,
                stream=True
            )

            if self._is_cancelled:
                self.cancelled.emit()
                return

            self.finished.emit(response)

        except Exception as e:
            self.error.emit(str(e))


class CodeImproveWorker(QThread):
    """Qt-friendly streaming worker for code improvement."""
    
    # Signals
    token = pyqtSignal(str)  # Emitted for each token/chunk
    finished = pyqtSignal(str)  # Emitted with full code when done
    error = pyqtSignal(str)  # Emitted on error
    started = pyqtSignal()  # Emitted when processing starts
    
    def __init__(self, prompt: str, code: str, model: str, file_path: str = None):
        """Initialize the worker.
        
        Args:
            prompt: The improvement prompt
            code: The code to improve
            model: The model to use
            file_path: Optional file path for backup
        """
        super().__init__()
        self.prompt = prompt
        self.code = code
        self.model = model
        self.file_path = file_path
        self.full_code = ""
    
    def run(self):
        """Main worker thread execution."""
        try:
            self.started.emit()
            
            # Create backup if file path is provided
            if self.file_path and os.path.exists(self.file_path):
                self.backup_file(self.file_path)
            
            # Prepare the full prompt with code context
            full_prompt = f"""
Please improve the following code based on this request: {self.prompt}

Original code:
```
{self.code}
```

Provide the improved code:
"""
            
            # Use generate_code_stream for streaming
            self.full_code = ""
            
            for chunk in generate_code_stream(full_prompt, self.model):
                # Check for interruption
                if self.isInterruptionRequested():
                    return
                
                # Emit token and build full code
                self.token.emit(chunk)
                self.full_code += chunk
            
            # Check for interruption before finishing
            if self.isInterruptionRequested():
                return
            
            # Emit finished signal with full code
            self.finished.emit(self.full_code)
            
        except Exception as e:
            if not self.isInterruptionRequested():
                self.error.emit(f"Error during code improvement: {str(e)}")
    
    @staticmethod
    def backup_file(file_path: str) -> str:
        """Create a backup of the original file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            str: Path to the backup file
            
        Raises:
            OSError: If backup creation fails
        """
        if not os.path.exists(file_path):
            raise OSError(f"File not found: {file_path}")
        
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(file_path), ".backup", timestamp)
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup file path
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, filename)
        
        # Copy file to backup location
        shutil.copy2(file_path, backup_path)
        
        return backup_path


class ThreadManager:
    _instance = None
    _executor = ThreadPoolExecutor()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThreadManager, cls).__new__(cls)
        return cls._instance

    def start_worker(self, worker):
        self._executor.submit(worker.run)

    def shutdown(self):
        self._executor.shutdown(wait=True)

