import os
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QLineEdit, QComboBox, 
    QHBoxLayout, QLabel, QSplitter, QScrollArea, QFrame, QTextBrowser,
    QApplication, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QIcon, QTextCursor
from ollama_client import generate_code, list_models, generate_code_stream
from llm_workers import LLMStreamWorker

class MessageWidget(QFrame):
    """Widget personalizado para mensagens do chat."""
    
    def __init__(self, message, is_user=True, timestamp=None):
        super().__init__()
        self.is_user = is_user
        self.setup_ui(message, timestamp)
    
    def setup_ui(self, message, timestamp):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)
        
        # Header com timestamp
        header_layout = QHBoxLayout()
        
        # Avatar/Ícone
        avatar_label = QLabel()
        if self.is_user:
            avatar_label.setText("👤")
            avatar_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #10a37f, stop: 1 #0d8a6c);
                    color: white;
                    border-radius: 16px;
                    padding: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 32px;
                    max-width: 32px;
                    min-height: 32px;
                    max-height: 32px;
                }
            """)
        else:
            avatar_label.setText("🤖")
            avatar_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #6366f1, stop: 1 #4f46e5);
                    color: white;
                    border-radius: 16px;
                    padding: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 32px;
                    max-width: 32px;
                    min-height: 32px;
                    max-height: 32px;
                }
            """)
        
        # Nome do remetente
        sender_label = QLabel("Você" if self.is_user else "KutsakAI")
        sender_label.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-weight: 600;
                font-size: 14px;
                padding-left: 8px;
            }
        """)
        
        # Timestamp
        if not timestamp:
            timestamp = datetime.datetime.now().strftime("%H:%M")
        time_label = QLabel(timestamp)
        time_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 11px;
                padding-left: 8px;
            }
        """)
        
        header_layout.addWidget(avatar_label)
        header_layout.addWidget(sender_label)
        header_layout.addWidget(time_label)
        header_layout.addStretch()
        
        # Mensagem
        message_widget = QTextBrowser()
        message_widget.setPlainText(message)
        message_widget.setMaximumHeight(200)
        message_widget.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                border: none;
                color: #e6e6e6;
                font-size: 13px;
                line-height: 1.5;
                padding: 8px 12px;
                margin-left: 40px;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(message_widget)
        
        # Styling do container
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #1f2937, stop: 1 #1a202c);
                    border-radius: 12px;
                    margin: 8px 0;
                    border-left: 3px solid #10a37f;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #2d3748, stop: 1 #252d3a);
                    border-radius: 12px;
                    margin: 8px 0;
                    border-left: 3px solid #6366f1;
                }
            """)

class TypingIndicator(QFrame):
    """Indicador de digitação animado."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_animation()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        
        # Avatar
        avatar = QLabel("🤖")
        avatar.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #6366f1, stop: 1 #4f46e5);
                color: white;
                border-radius: 16px;
                padding: 8px;
                font-size: 14px;
                min-width: 32px;
                max-width: 32px;
                min-height: 32px;
                max-height: 32px;
            }
        """)
        
        # Dots
        self.dots = [QLabel("●") for _ in range(3)]
        for i, dot in enumerate(self.dots):
            dot.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 16px;
                    padding: 0 2px;
                }
            """)
        
        layout.addWidget(avatar)
        layout.addWidget(QLabel("KutsakAI está digitando"))
        for dot in self.dots:
            layout.addWidget(dot)
        layout.addStretch()
        
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2d3748, stop: 1 #252d3a);
                border-radius: 12px;
                margin: 8px 0;
                border-left: 3px solid #6366f1;
            }
        """)
    
    def setup_animation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_dots)
        self.current_dot = 0
        
    def start_animation(self):
        self.timer.start(500)
        
    def stop_animation(self):
        self.timer.stop()
        
    def animate_dots(self):
        for dot in self.dots:
            dot.setStyleSheet("""
                QLabel {
                    color: #888888;
                    font-size: 16px;
                    padding: 0 2px;
                }
            """)
        
        self.dots[self.current_dot].setStyleSheet("""
            QLabel {
                color: #10a37f;
                font-size: 18px;
                padding: 0 2px;
            }
        """)
        
        self.current_dot = (self.current_dot + 1) % 3

class GenerationWorker(QThread):
    """Worker thread para geração de código."""
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, prompt, model):
        super().__init__()
        self.prompt = prompt
        self.model = model
    
    def run(self):
        try:
            response = generate_code(self.prompt, model=self.model)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class ChatGUI(QWidget):
    """Interface de chat moderna estilo ChatGPT."""
    
    def __init__(self):
        super().__init__()
        self.chat_history = []
        self.is_generating = False
        self.setup_ui()
        self.add_welcome_message()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.create_header()
        main_layout.addWidget(self.header)
        
        # Chat Area
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Main chat area
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(16, 16, 16, 16)
        
        # Messages scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(0)
        self.messages_layout.addStretch()
        
        self.scroll_area.setWidget(self.messages_widget)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)
        
        chat_layout.addWidget(self.scroll_area)
        
        # Input area
        self.create_input_area()
        chat_layout.addWidget(self.input_frame)
        
        content_layout.addWidget(chat_container, 3)
        
        # Sidebar
        self.create_sidebar()
        content_layout.addWidget(self.sidebar, 1)
        
        main_layout.addLayout(content_layout)
    
    def create_header(self):
        self.header = QFrame()
        self.header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1a1a1a, stop: 1 #151515);
                border-bottom: 1px solid #2a2a2a;
                padding: 16px;
            }
        """)
        
        header_layout = QHBoxLayout(self.header)
        
        # Título
        title = QLabel("💬 KutsakAI Chat")
        title.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 18px;
                font-weight: 600;
            }
        """)
        
        # Status
        self.status_label = QLabel("🟢 Conectado")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #10a37f;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
    
    def create_input_area(self):
        self.input_frame = QFrame()
        self.input_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                border: 1px solid #3a3a3a;
                border-radius: 16px;
                padding: 12px;
                margin: 16px 0;
            }
        """)
        
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(8, 8, 8, 8)
        
        # Input field
        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Digite sua mensagem aqui... (pressione Enter para enviar)")
        self.prompt_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #e6e6e6;
                font-size: 14px;
                padding: 8px 12px;
            }
        """)
        self.prompt_input.returnPressed.connect(self.on_send)
        
        # Send button
        self.send_button = QPushButton("📤")
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #10a37f, stop: 1 #0d8a6c);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px;
                font-size: 16px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #0d8a6c, stop: 1 #0a6b4f);
            }
            QPushButton:disabled {
                background: #404040;
                color: #808080;
            }
        """)
        self.send_button.clicked.connect(self.on_send)
        
        input_layout.addWidget(self.prompt_input)
        input_layout.addWidget(self.send_button)
    
    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #151515, stop: 1 #1a1a1a);
                border-left: 1px solid #2a2a2a;
                padding: 16px;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        # Provider section
        provider_label = QLabel("🌐 Provedor LLM")
        provider_label.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 8px;
            }
        """)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Ollama", "OpenRouter", "NVIDIA", "Custom"])
        self.provider_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2a2a2a, stop: 1 #252525);
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                margin-bottom: 16px;
            }
        """)
        
        # Model section
        model_label = QLabel("🤖 Modelo IA")
        model_label.setStyleSheet(provider_label.styleSheet())
        
        self.model_combo = QComboBox()
        try:
            models = list_models()
            self.model_combo.addItems(models)
            if not models:
                self.model_combo.addItem("Nenhum modelo disponível")
        except:
            self.model_combo.addItem("Erro ao carregar modelos")
        
        # Connect provider change to model list update
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        self.model_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2a2a2a, stop: 1 #252525);
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }
        """)
        
        # Stats section
        stats_label = QLabel("📊 Estatísticas")
        stats_label.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 14px;
                font-weight: 600;
                margin: 24px 0 8px 0;
            }
        """)
        
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.messages_count = QLabel("Mensagens: 0")
        self.session_time = QLabel("Sessão: 00:00")
        
        for label in [self.messages_count, self.session_time]:
            label.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font-size: 12px;
                    padding: 4px 0;
                }
            """)
        
        stats_layout.addWidget(self.messages_count)
        stats_layout.addWidget(self.session_time)
        
        # Actions section
        actions_label = QLabel("⚡ Ações")
        actions_label.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 14px;
                font-weight: 600;
                margin: 24px 0 8px 0;
            }
        """)
        
        self.clear_button = QPushButton("🗑️ Limpar Chat")
        self.export_button = QPushButton("💾 Exportar")
        
        for button in [self.clear_button, self.export_button]:
            button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #2a2a2a, stop: 1 #252525);
                    color: #e6e6e6;
                    border: 1px solid #3a3a3a;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    text-align: left;
                    margin: 2px 0;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #353535, stop: 1 #2f2f2f);
                }
            """)
        
        self.clear_button.clicked.connect(self.clear_chat)
        self.export_button.clicked.connect(self.export_chat)
        
        # Layout
        sidebar_layout.addWidget(provider_label)
        sidebar_layout.addWidget(self.provider_combo)
        sidebar_layout.addWidget(model_label)
        sidebar_layout.addWidget(self.model_combo)
        sidebar_layout.addWidget(stats_label)
        sidebar_layout.addWidget(self.stats_widget)
        sidebar_layout.addWidget(actions_label)
        sidebar_layout.addWidget(self.clear_button)
        sidebar_layout.addWidget(self.export_button)
        sidebar_layout.addStretch()
    
    def add_welcome_message(self):
        welcome_text = """👋 Olá! Eu sou o KutsakAI, seu assistente de desenvolvimento web.

Posso ajudar você com:
• Geração de código HTML, CSS e JavaScript
• Criação de componentes web
• Otimização e melhorias de código
• Resolução de problemas de desenvolvimento
• Sugestões de design e UX

Como posso ajudar você hoje?"""
        
        self.add_message(welcome_text, is_user=False)
    
    def add_message(self, message, is_user=True, timestamp=None):
        message_widget = MessageWidget(message, is_user, timestamp)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message_widget)
        
        # Animar entrada da mensagem
        self.animate_message(message_widget)
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # Update stats
        self.update_stats()
    
    def animate_message(self, widget):
        # Animação simples de fade in
        widget.setProperty("opacity", 0.0)
        
        self.animation = QPropertyAnimation(widget, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
    
    def scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_stats(self):
        count = len([msg for msg in self.chat_history if msg.get('is_user', True)])
        self.messages_count.setText(f"Mensagens: {count}")
    
    def show_typing_indicator(self):
        if not hasattr(self, 'typing_indicator'):
            self.typing_indicator = TypingIndicator()
        
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, self.typing_indicator)
        self.typing_indicator.start_animation()
        self.scroll_to_bottom()
    
    def hide_typing_indicator(self):
        if hasattr(self, 'typing_indicator'):
            self.typing_indicator.stop_animation()
            self.messages_layout.removeWidget(self.typing_indicator)
            self.typing_indicator.deleteLater()
            del self.typing_indicator
    
    def on_send(self):
        # QLineEdit uses text(), not toPlainText()
        if hasattr(self.prompt_input, 'toPlainText'):
            prompt = self.prompt_input.toPlainText().strip()
        else:
            prompt = self.prompt_input.text().strip()
        if not prompt or self.is_generating:
            return
        
        # Add user message
        self.add_message(prompt, is_user=True)
        self.chat_history.append({'message': prompt, 'is_user': True, 'timestamp': datetime.datetime.now()})
        self.prompt_input.clear()
        
        # Show typing indicator
        self.show_typing_indicator()
        
        # Disable input
        self.is_generating = True
        self.send_button.setEnabled(False)
        self.prompt_input.setEnabled(False)
        self.status_label.setText("🔄 Gerando resposta...")
        
        # Generate response
        model = self.model_combo.currentText()
        self.worker = GenerationWorker(prompt, model)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.start()
    
    def on_generation_finished(self, response):
        self.hide_typing_indicator()
        
        # Add AI response
        self.add_message(response, is_user=False)
        self.chat_history.append({'message': response, 'is_user': False, 'timestamp': datetime.datetime.now()})
        
        # Re-enable input
        self.is_generating = False
        self.send_button.setEnabled(True)
        self.prompt_input.setEnabled(True)
        self.prompt_input.setFocus()
        self.status_label.setText("🟢 Conectado")
    
    def on_generation_error(self, error):
        self.hide_typing_indicator()
        
        error_message = f"❌ Erro ao gerar resposta: {error}"
        self.add_message(error_message, is_user=False)
        
        # Re-enable input
        self.is_generating = False
        self.send_button.setEnabled(True)
        self.prompt_input.setEnabled(True)
        self.status_label.setText("🔴 Erro na conexão")
    
    def clear_chat(self):
        # Clear messages
        for i in reversed(range(self.messages_layout.count())):
            child = self.messages_layout.itemAt(i).widget()
            if child and isinstance(child, (MessageWidget, TypingIndicator)):
                child.deleteLater()
        
        self.chat_history.clear()
        self.add_welcome_message()
        self.update_stats()
    
    def export_chat(self):
        if not self.chat_history:
            QMessageBox.information(self, "Exportar Chat", "Não há mensagens para exportar.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar Chat", 
            f"chat_kutsakai_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("KutsakAI Chat Export\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for msg in self.chat_history:
                        sender = "Usuário" if msg['is_user'] else "KutsakAI"
                        timestamp = msg['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] {sender}:\n")
                        f.write(f"{msg['message']}\n\n")
                
                QMessageBox.information(self, "Sucesso", f"Chat exportado para:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar chat:\n{str(e)}")

    def on_provider_changed(self, provider_name):
        """Atualiza o provedor ativo na configuração e recarrega modelos."""
        from config_manager import set_config
        set_config("providers.active", provider_name.lower())
        
        # Update model list based on provider
        self.model_combo.clear()
        if provider_name.lower() == "ollama":
            try:
                models = list_models()
                self.model_combo.addItems(models)
            except:
                self.model_combo.addItem("codellama")
        elif provider_name.lower() == "openrouter":
            self.model_combo.addItems([
                "anthropic/claude-3-opus", 
                "anthropic/claude-3.5-sonnet",
                "openai/gpt-4o",
                "google/gemini-pro-1.5"
            ])
        elif provider_name.lower() == "nvidia":
            self.model_combo.addItems([
                "nvidia/llama-3.1-405b-instruct",
                "nvidia/mistral-large-2-instruct"
            ])
        else:
            self.model_combo.addItem("default-model")
