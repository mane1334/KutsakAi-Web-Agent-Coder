import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSplitter, QTabWidget,
    QLineEdit, QTreeWidget, QListWidget, QFrame,
    QMessageBox, QFileDialog, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QIcon, QFont

from .panels.file_tree_panel import FileTreePanel
from .panels.preview_panel import PreviewPanel
from .panels.git_panel import GitPanel
from ..logic.editor_controller import EditorController
from site_generator.project_manager import ProjectManager

class EditorView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = EditorController(self)
        self.setup_ui()

    def setup_ui(self):
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        self.setWindowTitle('KutsakAI Web agent Builder')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'assets', 'kutsakai_icon.png')))
        
        layout = QVBoxLayout(self)
        
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)
        toolbar.setSpacing(10)

        project_group = QHBoxLayout()
        self.open_project_btn = QPushButton('Abrir Projeto')
        self.open_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        project_group.addWidget(self.open_project_btn)
        self.save_all_btn = QPushButton('Salvar Tudo')
        self.save_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        project_group.addWidget(self.save_all_btn)
        self.dashboard_btn = QPushButton('Dashboard')
        self.dashboard_btn.setStyleSheet("background-color: #007acc; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        self.dashboard_btn.setToolTip('Abrir dashboard de exemplos RAG')
        project_group.addWidget(self.dashboard_btn)
        self.project_path_label = QLabel('')
        self.project_path_label.setStyleSheet('color: #666; padding: 0 10px;')
        project_group.addWidget(self.project_path_label)
        self.edit_system_prompt_btn = QPushButton('Edit System Prompt')
        self.edit_system_prompt_btn.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 15px; border-radius: 4px; font-weight: bold;")
        project_group.addWidget(self.edit_system_prompt_btn)
        toolbar.addLayout(project_group)
        
        model_group = QHBoxLayout()
        model_group.addWidget(QLabel('Modelo:'))
        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #666;
                border-radius: 3px;
                min-width: 150px;
            }
        """)
        model_group.addWidget(self.model_combo)
        self.max_tokens_input = QLineEdit()
        self.max_tokens_input.setPlaceholderText('Max Tokens (ex: 2048)')
        self.max_tokens_input.setText('2048')
        self.max_tokens_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #666;
                border-radius: 3px;
                min-width: 100px;
            }
        """)
        model_group.addWidget(self.max_tokens_input)
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText('Temperatura (ex: 0.7)')
        self.temperature_input.setText('0.7')
        self.temperature_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #666;
                border-radius: 3px;
                min-width: 100px;
            }
        """)
        model_group.addWidget(self.temperature_input)
        toolbar.addLayout(model_group)

        self.improve_input = QLineEdit()
        self.improve_input.setPlaceholderText('Descreva as melhorias desejadas...')
        self.improve_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #666;
                border-radius: 3px;
                min-width: 300px;
            }
        """)
        self.improve_btn = QPushButton('✨ Melhorar com IA')
        self.improve_btn.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
        """)
        self.improve_all_btn = QPushButton('✨ Melhorar Todos Arquivos')
        self.improve_all_btn.setStyleSheet("background-color: #10a37f; color: white; padding: 8px 15px; border-radius: 4px;")
        self.improve_all_btn.setToolTip('Melhora todos os arquivos do projeto com IA')
        self.loop_ia_btn = QPushButton('🔁 Loop IA (5x)')
        self.loop_ia_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 8px 15px; border-radius: 4px;")
        self.loop_ia_btn.setToolTip('Executa a melhoria IA 5 vezes em sequência no arquivo atual')
        
        improve_row = QHBoxLayout()
        improve_row.addWidget(self.improve_input)
        improve_row.addWidget(self.improve_btn)
        improve_row.addWidget(self.improve_all_btn)
        improve_row.addWidget(self.loop_ia_btn)
        improve_row.addStretch()
        
        layout.addLayout(toolbar)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        
        self.file_tree_panel = FileTreePanel()
        main_splitter.addWidget(self.file_tree_panel)
        
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background: #2d2d2d;
                color: #d4d4d4;
                padding: 8px 15px;
                border-top: 2px solid transparent;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
                border-top: 2px solid #10a37f;
            }
        """)
        editor_layout.addWidget(self.editor_tabs)
        
        main_splitter.addWidget(editor_container)
        
        self.preview_panel = PreviewPanel()
        main_splitter.addWidget(self.preview_panel)
        
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        main_splitter.setStretchFactor(2, 1)
        
        layout.addWidget(main_splitter)
        layout.addLayout(improve_row)

        panels_row = QHBoxLayout()
        
        snippets_col = QVBoxLayout()
        snippets_col.addWidget(QLabel('Snippets Customizáveis:'))
        self.snippets_panel = QListWidget()
        self.snippets_panel.setMinimumHeight(80)
        self.snippets_panel.setMaximumHeight(200)
        self.snippets_panel.setStyleSheet("background: #23272e; color: #d4d4d4; border: none; font-size: 12px;")
        snippets_col.addWidget(self.snippets_panel)
        snippet_btns = QHBoxLayout()
        self.add_snippet_btn = QPushButton('Adicionar Snippet')
        self.remove_snippet_btn = QPushButton('Remover Snippet')
        snippet_btns.addWidget(self.add_snippet_btn)
        snippet_btns.addWidget(self.remove_snippet_btn)
        snippets_col.addLayout(snippet_btns)
        panels_row.addLayout(snippets_col)
        
        self.git_panel = GitPanel()
        panels_row.addWidget(self.git_panel)

        plugins_col = QVBoxLayout()
        plugins_col.addWidget(QLabel('Plugins carregados:'))
        self.plugins_panel = QListWidget()
        self.plugins_panel.setMinimumHeight(60)
        self.plugins_panel.setMaximumHeight(120)
        self.plugins_panel.setStyleSheet("background: #23272e; color: #aaccff; border: none; font-size: 12px;")
        plugins_col.addWidget(self.plugins_panel)
        panels_row.addLayout(plugins_col)
        layout.addLayout(panels_row)
        
        self.problems_panel = QListWidget()
        self.problems_panel.setMinimumHeight(80)
        self.problems_panel.setMaximumHeight(200)
        self.problems_panel.setStyleSheet("background: #2d2d2d; color: #ffcccc; border: none; font-size: 12px;")
        layout.addWidget(self.problems_panel)

        self.file_tree_panel.file_tree.itemDoubleClicked.connect(self.on_file_tree_double_click)
        self.open_project_btn.clicked.connect(self.on_open_project)
        self.save_all_btn.clicked.connect(self.on_save_all)
        self.dashboard_btn.clicked.connect(self.on_dashboard)
        self.edit_system_prompt_btn.clicked.connect(self.controller.edit_system_prompt)
        self.improve_btn.clicked.connect(self.on_improve)
        self.improve_all_btn.clicked.connect(self.on_improve_all)
        self.loop_ia_btn.clicked.connect(self.on_loop_ia)
        self.add_snippet_btn.clicked.connect(self.on_add_snippet)
        self.remove_snippet_btn.clicked.connect(self.on_remove_snippet)

    def create_tab(self, file_path):
        from .custom_editor_widget import VSCTextEdit
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0,0,0,0)
        editor = VSCTextEdit(self.controller.doc_keywords)
        tab.editor = editor
        tab.file_path = file_path
        layout.addWidget(editor)
        editor.load_content()
        return tab

    def show_status_message(self, message):
        QMessageBox.information(self, 'Status', message)

    def on_file_tree_double_click(self, item, column=0):
        caminho = self.project_path_label.text().strip()
        if not caminho:
            self.show_status_message('Nenhum projeto aberto!')
            return
        rel_path = item.text(0)
        file_path = os.path.join(caminho, rel_path)
        if not os.path.isfile(file_path):
            self.show_status_message('Arquivo não encontrado!')
            return
        # Abrir arquivo em nova aba
        tab = self.create_tab(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            tab.editor.setPlainText(conteudo)
            self.editor_tabs.addTab(tab, os.path.basename(file_path))
            self.editor_tabs.setCurrentWidget(tab)
            self.update_preview()
        except Exception as e:
            self.show_status_message(f'Erro ao abrir arquivo: {e}')

    def on_open_project(self):
        caminho = QFileDialog.getExistingDirectory(self, 'Escolha a pasta do projeto')
        if caminho:
            self.project_path_label.setText(caminho)
            self.show_status_message(f'Projeto aberto: {caminho}')
            pm = ProjectManager()
            try:
                # Popular árvore de arquivos com todos os arquivos
                self.file_tree_panel.file_tree.clear()
                total_arquivos = 0
                for pasta, _, arquivos in os.walk(caminho):
                    for arquivo in arquivos:
                        rel_path = os.path.relpath(os.path.join(pasta, arquivo), caminho)
                        item = QTreeWidgetItem([rel_path])
                        self.file_tree_panel.file_tree.addTopLevelItem(item)
                        total_arquivos += 1
                self.show_status_message(f'{total_arquivos} arquivos encontrados no projeto.')
                # Abrir arquivos principais nas abas
                self.editor_tabs.clear()
                conteudos = pm.load_project(caminho)
                opened = 0
                for tipo, conteudo in conteudos.items():
                    if conteudo:
                        if tipo == 'html':
                            file_path = os.path.join(caminho, 'index.html')
                        elif tipo == 'css':
                            file_path = os.path.join(caminho, 'css', 'styles.css')
                        elif tipo == 'js':
                            file_path = os.path.join(caminho, 'js', 'main.js')
                        else:
                            continue
                        tab = self.create_tab(file_path)
                        tab.editor.setPlainText(conteudo)
                        self.editor_tabs.addTab(tab, tipo.upper())
                        opened += 1
                if opened == 0:
                    self.show_status_message('Nenhum arquivo principal (index.html, styles.css, main.js) encontrado!')
                else:
                    self.show_status_message(f'{opened} arquivos principais abertos nas abas.')
                self.update_preview()
            except Exception as e:
                self.show_status_message(f'Erro ao carregar projeto: {e}')

    def on_save_all(self):
        caminho = self.project_path_label.text().strip()
        if not caminho:
            self.show_status_message('Nenhum projeto aberto!')
            return
        pm = ProjectManager()
        pm.current_project = caminho
        for i in range(self.editor_tabs.count()):
            tab = self.editor_tabs.widget(i)
            file_path = getattr(tab, 'file_path', None)
            if file_path and hasattr(tab, 'editor'):
                conteudo = tab.editor.toPlainText()
                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                except Exception as e:
                    self.show_status_message(f'Erro ao salvar {file_path}: {e}')
        self.show_status_message('Todos os arquivos foram salvos!')
        self.update_preview()

    def update_preview(self):
        # Atualiza o preview se for HTML
        if hasattr(self, 'preview_panel') and hasattr(self.preview_panel, 'site_preview'):
            caminho = self.project_path_label.text().strip()
            html_path = os.path.join(caminho, 'index.html')
            if os.path.exists(html_path):
                self.preview_panel.site_preview.load(f'file:///{html_path.replace(os.sep, "/")}')

    def on_improve(self):
        from ollama_client import generate_code
        aba = self.editor_tabs.currentWidget()
        if not aba or not hasattr(aba, 'editor') or not hasattr(aba, 'file_path'):
            self.show_status_message('Nenhum arquivo selecionado!')
            return
        prompt = self.improve_input.text().strip()
        if not prompt:
            self.show_status_message('Digite um prompt de melhoria!')
            return
        conteudo = aba.editor.toPlainText()
        model = self.model_combo.currentText() if hasattr(self, 'model_combo') else 'qwen2.5-coder:3b'
        try:
            improved = generate_code(prompt + '\n' + conteudo, model=model)
            aba.editor.setPlainText(improved)
            self.show_status_message('Arquivo melhorado com IA!')
            self.update_preview()
        except Exception as e:
            self.show_status_message(f'Erro ao melhorar arquivo: {e}')

    def on_improve_all(self):
        from ollama_client import generate_code
        prompt = self.improve_input.text().strip()
        if not prompt:
            self.show_status_message('Digite um prompt de melhoria!')
            return
        model = self.model_combo.currentText() if hasattr(self, 'model_combo') else 'qwen2.5-coder:3b'
        for i in range(self.editor_tabs.count()):
            tab = self.editor_tabs.widget(i)
            if hasattr(tab, 'editor'):
                conteudo = tab.editor.toPlainText()
                try:
                    improved = generate_code(prompt + '\n' + conteudo, model=model)
                    tab.editor.setPlainText(improved)
                except Exception as e:
                    self.show_status_message(f'Erro ao melhorar: {e}')
        self.show_status_message('Todos os arquivos melhorados com IA!')
        self.update_preview()

    def on_loop_ia(self):
        from ollama_client import generate_code
        aba = self.editor_tabs.currentWidget()
        if not aba or not hasattr(aba, 'editor') or not hasattr(aba, 'file_path'):
            self.show_status_message('Nenhum arquivo selecionado!')
            return
        prompt = self.improve_input.text().strip()
        if not prompt:
            self.show_status_message('Digite um prompt de melhoria!')
            return
        conteudo = aba.editor.toPlainText()
        model = self.model_combo.currentText() if hasattr(self, 'model_combo') else 'qwen2.5-coder:3b'
        try:
            for _ in range(5):
                conteudo = generate_code(prompt + '\n' + conteudo, model=model)
            aba.editor.setPlainText(conteudo)
            self.show_status_message('Loop IA concluído!')
            self.update_preview()
        except Exception as e:
            self.show_status_message(f'Erro no loop IA: {e}')

    def on_add_snippet(self):
        texto = self.improve_input.text().strip()
        if texto:
            self.snippets_panel.addItem(texto)
            self.improve_input.clear()
            self.show_status_message('Snippet adicionado!')
        else:
            self.show_status_message('Digite um texto para adicionar como snippet.')

    def on_remove_snippet(self):
        idx = self.snippets_panel.currentRow()
        if idx >= 0:
            self.snippets_panel.takeItem(idx)
            self.show_status_message('Snippet removido!')
        else:
            self.show_status_message('Selecione um snippet para remover.')

    def on_dashboard(self):
        try:
            from .dialogs.rag_dashboard_dialog import RAGDashboard
            dlg = RAGDashboard(self)
            dlg.exec()
        except Exception as e:
            self.show_status_message(f'Erro ao abrir dashboard: {e}')
