"""
Interface para geração de sites usando IA.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QMessageBox, QFileDialog, QProgressBar, QStatusBar,
    QFrame, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ollama_client import list_models, generate_code
from .project_manager import ProjectManager
from .sound_manager import sound_manager
from llm_workers import LLMWorker, ThreadManager

class SiteGeneratorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self.thread_manager = ThreadManager()
        self.workers = {}
        self.results = {}
        self.workers_finished = 0
        self.total_workers = 3
        # Carregar som de notificação
        sound_manager.load_sound('done', os.path.join(os.path.dirname(__file__), 'sounds', 'notification.wav'))
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do gerador com design moderno."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)
        
        # Header Section
        self.create_header()
        main_layout.addWidget(self.header_frame)
        
        # Content Card
        self.create_content_card()
        main_layout.addWidget(self.content_card)
        
        # Footer
        self.create_footer()
        main_layout.addWidget(self.footer_frame)
        
        main_layout.addStretch()
    
    def create_header(self):
        """Cria o cabeçalho moderno."""
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #667eea, stop: 1 #764ba2);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 16px;
            }
        """)
        
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setSpacing(12)
        
        # Título principal
        title = QLabel("🚀 Gerador de Sites IA")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: 700;
                margin: 0;
                padding: 0;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Subtítulo
        subtitle = QLabel("Crie sites profissionais em segundos com inteligência artificial")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                font-weight: 400;
                margin: 0;
                padding: 0;
            }
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
    
    def create_content_card(self):
        """Cria o cartão de conteúdo principal."""
        self.content_card = QFrame()
        self.content_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                border: 1px solid #2a2a2a;
                border-radius: 16px;
                padding: 32px;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_card)
        content_layout.setSpacing(24)
        
        # Seção de configuração
        config_section = self.create_config_section()
        content_layout.addWidget(config_section)
        
        # Seção de entrada
        input_section = self.create_input_section()
        content_layout.addWidget(input_section)
        
        # Seção de opções avançadas
        advanced_section = self.create_advanced_section()
        content_layout.addWidget(advanced_section)
        
        # Botão de geração
        generate_section = self.create_generate_section()
        content_layout.addWidget(generate_section)
        
        # Área de status
        status_section = self.create_status_section()
        content_layout.addWidget(status_section)
    
    def create_config_section(self):
        """Cria a seção de configuração."""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(16)
        
        # Título da seção
        section_title = QLabel("⚙️ Configurações")
        section_title.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
        """)
        
        # Container de modelos
        model_container = QFrame()
        model_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2a2a2a, stop: 1 #252525);
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        model_layout = QHBoxLayout(model_container)
        
        # Provider Selection
        provider_label = QLabel("🌐 Provedor:")
        provider_label.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Ollama", "OpenRouter", "NVIDIA", "Custom"])
        self.provider_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                min-width: 150px;
                margin-right: 20px;
            }
        """)
        
        model_label = QLabel("🤖 Modelo IA:")
        model_label.setStyleSheet(provider_label.styleSheet())
        
        self.model_combo = QComboBox()
        try:
            models = list_models()
            self.model_combo.addItems(models)
            if not models:
                self.model_combo.addItem("Nenhum modelo disponível")
        except:
            self.model_combo.addItem("Erro ao carregar modelos")
        
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        self.model_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                color: #e6e6e6;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
                min-width: 200px;
            }
            QComboBox:hover {
                border-color: #10a37f;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 4px solid transparent;
                border-top: 6px solid #999999;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background: #1f1f1f;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                color: #e6e6e6;
                selection-background-color: #10a37f;
            }
        """)
        
        model_layout.addWidget(provider_label)
        model_layout.addWidget(self.provider_combo)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        
        layout.addWidget(section_title)
        layout.addWidget(model_container)
        
        return section
    
    def create_input_section(self):
        """Cria a seção de entrada de dados."""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(16)
        
        # Título da seção
        section_title = QLabel("💭 Descrição do Site")
        section_title.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
        """)
        
        # Instrução
        instruction = QLabel("Descreva detalhadamente o site que você deseja criar:")
        instruction.setStyleSheet("""
            QLabel {
                color: #999999;
                font-size: 14px;
                margin-bottom: 8px;
            }
        """)
        
        # Campo de entrada
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("""
Exemplo detalhado:

"Criar uma landing page moderna para uma loja de roupas femininas chamada 'Style & Co'. 
Incluir:
• Header com logo e menu de navegação
• Seção hero com imagem de destaque e call-to-action
• Galeria de produtos em grid
• Seção sobre a empresa
• Footer com links sociais e informações de contato

Estilo: Moderno, minimalista, cores suaves (rosa e branco)
Layout: Responsivo para mobile e desktop""")
        
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #1f1f1f, stop: 1 #1a1a1a);
                color: #e6e6e6;
                border: 2px solid #3a3a3a;
                border-radius: 12px;
                padding: 16px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                min-height: 120px;
                max-height: 200px;
            }
            QTextEdit:focus {
                border: 2px solid #10a37f;
                box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.2);
            }
        """)
        
        layout.addWidget(section_title)
        layout.addWidget(instruction)
        layout.addWidget(self.prompt_input)
        
        return section
    
    def create_advanced_section(self):
        """Cria a seção de opções avançadas."""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(16)
        
        # Título da seção
        section_title = QLabel("🔧 Opções Avançadas")
        section_title.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
            }
        """)
        
        # Container de opções
        options_container = QFrame()
        options_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2a2a2a, stop: 1 #252525);
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        options_layout = QVBoxLayout(options_container)
        options_layout.setSpacing(16)
        
        # Framework CSS
        framework_layout = QHBoxLayout()
        framework_label = QLabel("🎨 Framework CSS:")
        framework_label.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 14px;
                font-weight: 500;
                min-width: 120px;
            }
        """)
        
        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["CSS Vanilla", "Bootstrap 5", "Tailwind CSS", "Material Design", "DaisyUI", "Flowbite", "Chakra UI"])
        self.framework_combo.setStyleSheet(self.model_combo.styleSheet())
        
        framework_layout.addWidget(framework_label)
        framework_layout.addWidget(self.framework_combo)
        framework_layout.addStretch()
        
        # Tipo de site
        site_type_layout = QHBoxLayout()
        site_type_label = QLabel("📄 Tipo de Site:")
        site_type_label.setStyleSheet(framework_label.styleSheet())
        
        self.site_type_combo = QComboBox()
        self.site_type_combo.addItems([
            "Landing Page Modern", "SaaS Landing", "Portfolio Minimal", "Blog Personal", "E-commerce Store", 
            "Corporate Portal", "Admin Dashboard", "API Documentation", "Product Launch"
        ])
        self.site_type_combo.setStyleSheet(self.model_combo.styleSheet())
        
        site_type_layout.addWidget(site_type_label)
        site_type_layout.addWidget(self.site_type_combo)
        site_type_layout.addStretch()
        
        # Opções de funcionalidades
        features_label = QLabel("✨ Funcionalidades Extras:")
        features_label.setStyleSheet("""
            QLabel {
                color: #e6e6e6;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 8px;
            }
        """)
        
        features_layout = QHBoxLayout()
        
        self.responsive_check = QCheckBox("📱 Responsivo")
        self.animations_check = QCheckBox("🎬 Animações CSS")
        self.forms_check = QCheckBox("📝 Formulários")
        self.seo_check = QCheckBox("🔍 Otimização SEO")
        
        for checkbox in [self.responsive_check, self.animations_check, self.forms_check, self.seo_check]:
            checkbox.setChecked(True)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #e6e6e6;
                    font-size: 13px;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid #3a3a3a;
                    background: #1f1f1f;
                }
                QCheckBox::indicator:checked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #10a37f, stop: 1 #0d8a6c);
                    border-color: #10a37f;
                }
                QCheckBox::indicator:checked::after {
                    content: "✓";
                    color: white;
                    font-weight: bold;
                }
            """)
        
        features_layout.addWidget(self.responsive_check)
        features_layout.addWidget(self.animations_check)
        features_layout.addWidget(self.forms_check)
        features_layout.addWidget(self.seo_check)
        features_layout.addStretch()
        
        options_layout.addLayout(framework_layout)
        options_layout.addLayout(site_type_layout)
        options_layout.addWidget(features_label)
        options_layout.addLayout(features_layout)
        
        layout.addWidget(section_title)
        layout.addWidget(options_container)
        
        return section
    
    def create_generate_section(self):
        """Cria a seção do botão de geração."""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botão principal
        self.generate_btn = QPushButton()
        self.update_generate_button(False)
        self.generate_btn.clicked.connect(self.on_generate)
        
        layout.addWidget(self.generate_btn)
        
        return section
    
    def update_generate_button(self, is_generating=False):
        """Atualiza o estado do botão de geração."""
        if is_generating:
            self.generate_btn.setText("🔄 Gerando Site...")
            self.generate_btn.setEnabled(False)
            self.generate_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #6b7280, stop: 1 #4b5563);
                    color: white;
                    border: none;
                    padding: 16px 48px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    min-width: 200px;
                }
            """)
        else:
            self.generate_btn.setText("🚀 Gerar Site Agora")
            self.generate_btn.setEnabled(True)
            self.generate_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #10a37f, stop: 1 #0d8a6c);
                    color: white;
                    border: none;
                    padding: 16px 48px;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: 600;
                    min-width: 200px;
                    box-shadow: 0 4px 16px rgba(16, 163, 127, 0.3);
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #0d8a6c, stop: 1 #0a6b4f);
                    box-shadow: 0 6px 20px rgba(16, 163, 127, 0.4);
                    transform: translateY(-2px);
                }
                QPushButton:pressed {
                    transform: translateY(0px);
                    box-shadow: 0 2px 8px rgba(16, 163, 127, 0.2);
                }
            """)
    
    def create_status_section(self):
        """Cria a seção de status."""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #2a2a2a, stop: 1 #252525);
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        # Status label
        self.status_label = QLabel("Pronto para gerar")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #10a37f;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                text-align: center;
                color: #e6e6e6;
                font-size: 12px;
                font-weight: 500;
                height: 24px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #10a37f, stop: 1 #0d8a6c);
                border-radius: 6px;
                box-shadow: 0 0 10px rgba(16, 163, 127, 0.3);
            }
        """)
        
        # Time estimate
        self.time_estimate = QLabel("")
        self.time_estimate.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                text-align: center;
            }
        """)
        self.time_estimate.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.time_estimate)
        
        return section
    
    def create_footer(self):
        """Cria o rodapé."""
        self.footer_frame = QFrame()
        self.footer_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                padding: 16px;
            }
        """)
        
        footer_layout = QHBoxLayout(self.footer_frame)
        
        # Tips
        tips_label = QLabel("💡 Dica: Seja específico na descrição para obter melhores resultados")
        tips_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-style: italic;
            }
        """)
        
        # Version info
        version_label = QLabel("KutsakAI v2.0")
        version_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
            }
        """)
        
        footer_layout.addWidget(tips_label)
        footer_layout.addStretch()
        footer_layout.addWidget(version_label)
        
    def on_generate(self):
        """Gera o site baseado no prompt."""
        prompt = self.prompt_input.toPlainText()
        if not prompt:
            QMessageBox.warning(self, 'Atenção', 'Por favor, descreva o site que você quer criar.')
            return
            
        try:
            self.update_generate_button(True)
            self.status_label.setText('Gerando estrutura do projeto...')
            self.progress.setValue(10)
            
            # Preparar prompts para cada componente
            prompts = {
                'html': f"""
Como um especialista em HTML5 semântico, crie o código HTML para: {prompt}

Use:
- Tags HTML5 semânticas (header, nav, main, section, footer)
- Links para CSS (../css/styles.css) e JS (../js/main.js)
- Meta tags importantes
- Otimização SEO
- Código limpo e indentado

Responda APENAS com o código HTML.""",

                'css': f"""
Como um especialista em CSS moderno, crie o CSS para: {prompt}

Use:
- CSS moderno e responsivo
- Organização por componentes
- Media queries para responsividade
- Variáveis CSS para cores e tipografia
- Comentários nas seções principais

Responda APENAS com o código CSS.""",

                'js': f"""
Como um especialista em JavaScript moderno, crie o JavaScript para: {prompt}

Use:
- JavaScript moderno (ES6+)
- Funções reutilizáveis
- Interatividade adequada
- Comentários explicativos
- JavaScript puro (sem jQuery)

Responda APENAS com o código JavaScript."""
            }
            
            # Escolher pasta do projeto
            dir_path = QFileDialog.getExistingDirectory(self, 'Escolha a pasta para o projeto')
            if not dir_path:
                return
                
            # Criar projeto
            projeto_nome = "site_" + "".join(x for x in prompt.lower()[:30] if x.isalnum())
            self.project_manager.create_project(dir_path, projeto_nome)
            
            self.progress.setValue(30)
            
            # Gerar arquivos
            modelo = self.model_combo.currentText()
            
            html_code = generate_code(prompts['html'], model=modelo)
            css_code = generate_code(prompts['css'], model=modelo)
            js_code = generate_code(prompts['js'], model=modelo)
            
            # Salvar arquivos
            self.project_manager.save_files(html_code, css_code, js_code)
            self.project_manager.create_readme(prompt)
            
            self.progress.setValue(100)
            self.status_label.setText('Projeto gerado com sucesso!')
            
            # Tocar som de notificação
            sound_manager.play('done')
            
            # Perguntar se quer abrir
            reply = QMessageBox.question(
                self, 
                'Abrir Projeto?',
                'Deseja abrir o site no navegador?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                import webbrowser
                webbrowser.open(f"file://{os.path.join(self.project_manager.current_project, 'index.html')}")
                
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao gerar o projeto: {str(e)}')
            self.status.showMessage('Erro ao gerar o projeto')
            
        finally:
            self.generate_btn.setEnabled(True)

    def on_provider_changed(self, provider_name):
        """Atualiza o provedor ativo na configuração e recarrega modelos."""
        from config_manager import set_config
        from ollama_client import list_models
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
