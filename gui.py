import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QFrame, QSplashScreen, QProgressBar,
    QSystemTrayIcon, QMenu, QMenuBar, QToolBar, QStatusBar,
    QMessageBox, QStyleFactory, QCheckBox, QComboBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPalette, QColor, QFont, QAction
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings
import json
import time

# Adicionar o diretório atual ao PYTHONPATH para importações
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from site_generator import SiteGeneratorGUI, SiteEditorGUI, ChatGUI

class SplashScreen(QSplashScreen):
    """Tela de inicialização moderna."""
    def __init__(self):
        # Criar pixmap para splash
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor('#1e1e1e'))
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout do splash
        layout = QVBoxLayout()
        
        # Logo/Título
        title = QLabel('KutsakAI Web Agent Builder')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #10a37f;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        
        # Subtítulo
        subtitle = QLabel('Gerador de Sites com IA')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #d4d4d4;
                font-size: 14px;
                margin-bottom: 20px;
            }
        """)
        
        # Barra de progresso
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333;
                border-radius: 5px;
                text-align: center;
                background: #2d2d2d;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #10a37f;
                border-radius: 3px;
            }
        """)
        
        # Status
        self.status = QLabel('Inicializando...')
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 12px;
                padding: 10px;
            }
        """)
        
        # Widget container
        container = QWidget()
        container.setLayout(layout)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        
        # Substituir setCentralWidget por layout
        layout = QVBoxLayout(self)
        layout.addWidget(container)
    
    def update_progress(self, value, message):
        self.progress.setValue(value)
        self.status.setText(message)
        QApplication.processEvents()

class ThemeManager:
    """Gerenciador de temas da aplicação com Material Design 3 e responsividade."""
    
    @staticmethod
    def get_dark_theme():
        return """
        /* Material Design 3 Dark Theme with Enhanced Responsiveness */
        QWidget {
            background-color: #0f0f0f;
            color: #e6e6e6;
            font-family: 'Inter', 'Segoe UI Variable', 'SF Pro Display', 'Roboto', sans-serif;
            font-size: 13px;
            selection-background-color: #10a37f;
            selection-color: white;
        }
        
        /* Accessibility Improvements */
        QWidget:focus {
            outline: 2px solid #10a37f;
            outline-offset: 2px;
        }
        
        QWidget[accessibleName="high-contrast"] {
            border: 2px solid #10a37f;
        }
        
        /* Animation Support */
        QWidget {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Main Container */
        QMainWindow {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0f0f0f, stop: 1 #151515);
        }
        
        /* Tab Widget Modern Design */
        QTabWidget {
            background: transparent;
            border: none;
        }
        
        QTabWidget::pane {
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            margin-top: -1px;
        }
        
        QTabBar {
            background: transparent;
            border: none;
        }
        
        QTabBar::tab {
            background: transparent;
            color: #999999;
            padding: 14px 24px;
            margin-right: 4px;
            border-radius: 10px 10px 0 0;
            font-weight: 500;
            font-size: 14px;
            min-width: 120px;
            transition: all 0.3s ease;
        }
        
        QTabBar::tab:selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1a1a1a, stop: 1 #1f1f1f);
            color: #ffffff;
            border: 1px solid #2a2a2a;
            border-bottom: none;
            box-shadow: 0 -2px 8px rgba(16, 163, 127, 0.3);
        }
        
        QTabBar::tab:hover:!selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #252525, stop: 1 #2a2a2a);
            color: #e6e6e6;
        }
        
        /* Modern Menu Bar */
        QMenuBar {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1a1a1a, stop: 1 #151515);
            color: #e6e6e6;
            border: none;
            border-bottom: 1px solid #2a2a2a;
            padding: 4px 0;
        }
        
        QMenuBar::item {
            padding: 10px 16px;
            background: transparent;
            border-radius: 8px;
            margin: 2px 4px;
            font-weight: 500;
        }
        
        QMenuBar::item:selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #10a37f, stop: 1 #0d8a6c);
            color: white;
            box-shadow: 0 2px 8px rgba(16, 163, 127, 0.3);
        }
        
        QMenuBar::item:pressed {
            background: #0a6b4f;
        }
        
        /* Modern Menu */
        QMenu {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1f1f1f, stop: 1 #1a1a1a);
            color: #e6e6e6;
            border: 1px solid #3a3a3a;
            border-radius: 12px;
            padding: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }
        
        QMenu::item {
            padding: 12px 20px;
            border-radius: 8px;
            margin: 2px;
            font-size: 13px;
        }
        
        QMenu::item:selected {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #10a37f, stop: 1 #0d8a6c);
            color: white;
        }
        
        QMenu::separator {
            height: 1px;
            background: #3a3a3a;
            margin: 8px 16px;
        }
        
        /* Modern Toolbar */
        QToolBar {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1a1a1a, stop: 1 #151515);
            border: none;
            border-bottom: 1px solid #2a2a2a;
            spacing: 8px;
            padding: 8px 16px;
        }
        
        QToolBar QToolButton {
            background: transparent;
            color: #e6e6e6;
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 13px;
        }
        
        QToolBar QToolButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #2a2a2a, stop: 1 #252525);
        }
        
        QToolBar QToolButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #10a37f, stop: 1 #0d8a6c);
            color: white;
        }
        
        QToolBar::separator {
            background: #3a3a3a;
            width: 1px;
            margin: 8px 4px;
        }
        
        /* Modern Status Bar */
        QStatusBar {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #151515, stop: 1 #1a1a1a);
            color: #999999;
            border: none;
            border-top: 1px solid #2a2a2a;
            padding: 6px 16px;
            font-size: 12px;
        }
        
        QStatusBar QLabel {
            background: transparent;
            padding: 4px 8px;
            border-radius: 6px;
        }
        
        /* Modern Buttons */
        QPushButton {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #10a37f, stop: 1 #0d8a6c);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 13px;
            min-width: 100px;
            box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
        }
        
        QPushButton:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0d8a6c, stop: 1 #0a6b4f);
            box-shadow: 0 6px 16px rgba(16, 163, 127, 0.4);
            transform: translateY(-1px);
        }
        
        QPushButton:pressed {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #0a6b4f, stop: 1 #085a42);
            box-shadow: 0 2px 6px rgba(16, 163, 127, 0.2);
            transform: translateY(1px);
        }
        
        QPushButton:disabled {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #404040, stop: 1 #353535);
            color: #808080;
            box-shadow: none;
        }
        
        /* Secondary Button */
        QPushButton[class="secondary"] {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #2a2a2a, stop: 1 #252525);
            color: #e6e6e6;
            border: 1px solid #3a3a3a;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        
        QPushButton[class="secondary"]:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #353535, stop: 1 #2f2f2f);
            border-color: #4a4a4a;
        }
        
        /* Modern Frames */
        QFrame {
            background: transparent;
            border: none;
        }
        
        QFrame#sidebar {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #151515, stop: 1 #1a1a1a);
            border-right: 1px solid #2a2a2a;
        }
        
        QFrame#card {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1f1f1f, stop: 1 #1a1a1a);
            border: 1px solid #2a2a2a;
            border-radius: 12px;
            padding: 16px;
        }
        
        /* Modern Scrollbars */
        QScrollBar:vertical {
            background: transparent;
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }
        
        QScrollBar::handle:vertical {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #404040, stop: 1 #353535);
            min-height: 20px;
            border-radius: 6px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #4a4a4a, stop: 1 #404040);
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            background: transparent;
        }
        
        QScrollBar:horizontal {
            background: transparent;
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }
        
        QScrollBar::handle:horizontal {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #404040, stop: 1 #353535);
            min-width: 20px;
            border-radius: 6px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #4a4a4a, stop: 1 #404040);
        }
        
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0;
            background: transparent;
        }
        
        /* Modern Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1f1f1f, stop: 1 #1a1a1a);
            color: #e6e6e6;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 13px;
            selection-background-color: #10a37f;
        }
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #10a37f;
            box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.2);
        }
        
        /* Modern ComboBox */
        QComboBox {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #1f1f1f, stop: 1 #1a1a1a);
            color: #e6e6e6;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 13px;
            min-width: 120px;
        }
        
        QComboBox:hover {
            border-color: #4a4a4a;
        }
        
        QComboBox:focus {
            border: 2px solid #10a37f;
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
            padding: 4px;
        }
        
        /* Modern Progress Bar */
        QProgressBar {
            background: #2a2a2a;
            border: none;
            border-radius: 6px;
            text-align: center;
            color: #e6e6e6;
            font-size: 12px;
            font-weight: 500;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                      stop: 0 #10a37f, stop: 1 #0d8a6c);
            border-radius: 6px;
            box-shadow: 0 0 10px rgba(16, 163, 127, 0.3);
        }
        """
    
    @staticmethod
    def get_light_theme():
        return """
        QWidget {
            background-color: #ffffff;
            color: #333333;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QTabWidget::pane {
            border: 1px solid #ddd;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background: #f5f5f5;
            color: #333;
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
        }
        
        QTabBar::tab:selected {
            background: #ffffff;
            border-bottom: 3px solid #10a37f;
            color: #000;
        }
        
        QTabBar::tab:hover {
            background: #e9e9e9;
        }
        
        QPushButton {
            background: #10a37f;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background: #0d8a6c;
        }
        """

class SettingsManager:
    """Gerenciador de configurações da aplicação."""
    
    def __init__(self):
        self.settings = QSettings('KutsakAI', 'WebAgentBuilder')
        
    def get(self, key, default=None):
        return self.settings.value(key, default)
        
    def set(self, key, value):
        self.settings.setValue(key, value)
        
    def get_theme(self):
        return self.get('theme', 'dark')
        
    def set_theme(self, theme):
        self.set('theme', theme)
        
    def get_window_geometry(self):
        return self.get('window_geometry')
        
    def set_window_geometry(self, geometry):
        self.set('window_geometry', geometry)

class CoderAgentGUI(QWidget):
    """Interface principal moderna com recursos avançados."""
    
    def __init__(self):
        super().__init__()
        
        # Configurações
        self.settings_manager = SettingsManager()
        
        # Setup da interface
        self.setup_window()
        self.setup_ui()
        self.setup_theme()
        self.setup_system_tray()
        
        # Restaurar geometria
        self.restore_geometry()
        
    def setup_window(self):
        """Configura a janela principal."""
        self.setWindowTitle('KutsakAI Web Agent Builder v2.0')
        self.setMinimumSize(1000, 700)
        self.resize(1400, 900)
        
        # Ícone da aplicação
        icon_path = os.path.join(os.path.dirname(__file__), 'site_generator', 'assets', 'kutsakai_icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
    def setup_ui(self):
        """Configura a interface principal."""
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)
        
        # Menu bar
        self.setup_menu_bar()
        main_layout.addWidget(self.menu_bar)
        
        # Toolbar
        self.setup_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # Área principal com abas
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.setMovable(True)
        main_layout.addWidget(self.tabs)
        
        # Inicializar abas
        self.setup_tabs()
        
        # Status bar
        self.setup_status_bar()
        main_layout.addWidget(self.status_bar)
        
    def setup_menu_bar(self):
        """Configura a barra de menu."""
        self.menu_bar = QMenuBar()
        
        # Menu Arquivo
        file_menu = self.menu_bar.addMenu('&Arquivo')
        
        new_project_action = QAction('&Novo Projeto', self)
        new_project_action.setShortcut('Ctrl+N')
        new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction('&Abrir Projeto', self)
        open_project_action.setShortcut('Ctrl+O')
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction('&Configurações', self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('&Sair', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Visualizar
        view_menu = self.menu_bar.addMenu('&Visualizar')

        web_coder_action = QAction('💬 &Chat', self)
        web_coder_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(web_coder_action)

        view_menu.addSeparator()
        
        self.dark_theme_action = QAction('Tema &Escuro', self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.triggered.connect(lambda: self.change_theme('dark'))
        view_menu.addAction(self.dark_theme_action)
        
        self.light_theme_action = QAction('Tema &Claro', self)
        self.light_theme_action.setCheckable(True)
        self.light_theme_action.triggered.connect(lambda: self.change_theme('light'))
        view_menu.addAction(self.light_theme_action)
        
        # Menu Ajuda
        help_menu = self.menu_bar.addMenu('&Ajuda')
        
        about_action = QAction('&Sobre', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """Configura a barra de ferramentas."""
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Botão Novo Projeto
        new_action = QAction('🆕 Novo', self)
        new_action.setToolTip('Criar novo projeto (Ctrl+N)')
        new_action.triggered.connect(self.new_project)
        self.toolbar.addAction(new_action)
        
        # Botão Abrir
        open_action = QAction('📂 Abrir', self)
        open_action.setToolTip('Abrir projeto existente (Ctrl+O)')
        open_action.triggered.connect(self.open_project)
        self.toolbar.addAction(open_action)

        self.toolbar.addSeparator()

        # Botão Web Coder
        web_coder_action = QAction('💬 Chat', self)
        web_coder_action.setToolTip('Abrir o Chat')
        web_coder_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        self.toolbar.addAction(web_coder_action)
        
        self.toolbar.addSeparator()
        
        # Toggle Tema
        theme_action = QAction('🌙 Tema', self)
        theme_action.setToolTip('Alternar tema claro/escuro')
        theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(theme_action)
        
    def setup_tabs(self):
        """Configura as abas principais."""
        # Tab: Gerador de Sites
        self.generator = SiteGeneratorGUI()
        self.tabs.addTab(self.generator, '🚀 Gerador')
        
        # Tab: Editor de Sites
        self.editor = SiteEditorGUI()
        self.tabs.addTab(self.editor, '📝 Editor')

        # Tab: Web Coder
        self.web_coder = ChatGUI()
        self.tabs.addTab(self.web_coder, '💬 Chat')
        
    def setup_status_bar(self):
        """Configura a barra de status."""
        self.status_bar = QStatusBar()
        
        # Status principal
        self.status_label = QLabel('Pronto')
        self.status_bar.addWidget(self.status_label)
        
        # Informações do projeto
        self.project_info = QLabel('Nenhum projeto')
        self.status_bar.addPermanentWidget(self.project_info)
        
        # Tema atual
        self.theme_info = QLabel(f'Tema: {self.settings_manager.get_theme().title()}')
        self.status_bar.addPermanentWidget(self.theme_info)
        
    def setup_theme(self):
        """Aplica o tema salvo."""
        theme = self.settings_manager.get_theme()
        self.apply_theme(theme)
        
    def setup_system_tray(self):
        """Configura o ícone na bandeja do sistema."""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            
            # Ícone
            icon_path = os.path.join(os.path.dirname(__file__), 'site_generator', 'assets', 'kutsakai_icon.png')
            if os.path.exists(icon_path):
                self.tray_icon.setIcon(QIcon(icon_path))
            
            # Menu do tray
            tray_menu = QMenu()
            
            show_action = QAction('Mostrar', self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            quit_action = QAction('Sair', self)
            quit_action.triggered.connect(QApplication.instance().quit)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.tray_icon_activated)
            self.tray_icon.show()
    
    def apply_theme(self, theme_name):
        """Aplica um tema específico."""
        if theme_name == 'dark':
            self.setStyleSheet(ThemeManager.get_dark_theme())
            self.dark_theme_action.setChecked(True)
            self.light_theme_action.setChecked(False)
        else:
            self.setStyleSheet(ThemeManager.get_light_theme())
            self.dark_theme_action.setChecked(False)
            self.light_theme_action.setChecked(True)
            
        self.theme_info.setText(f'Tema: {theme_name.title()}')
    
    def change_theme(self, theme_name):
        """Muda o tema e salva nas configurações."""
        self.apply_theme(theme_name)
        self.settings_manager.set_theme(theme_name)
        
    def toggle_theme(self):
        """Alterna entre tema claro e escuro."""
        current_theme = self.settings_manager.get_theme()
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        self.change_theme(new_theme)
    
    def restore_geometry(self):
        """Restaura a geometria da janela."""
        geometry = self.settings_manager.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
    
    def save_geometry(self):
        """Salva a geometria da janela."""
        self.settings_manager.set_window_geometry(self.saveGeometry())
    
    def new_project(self):
        """Cria um novo projeto."""
        self.tabs.setCurrentIndex(0)  # Vai para o gerador
        self.status_label.setText('Criando novo projeto...')
        
    def open_project(self):
        """Abre um projeto existente."""
        self.tabs.setCurrentIndex(1)  # Vai para o editor
        self.editor.on_open_project()
        self.status_label.setText('Abrindo projeto...')
    
    def show_settings(self):
        """Mostra o diálogo de configurações."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QSpinBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Configurações')
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Tema
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel('Tema:'))
        theme_combo = QComboBox()
        theme_combo.addItems(['Dark', 'Light'])
        theme_combo.setCurrentText(self.settings_manager.get_theme().title())
        theme_layout.addWidget(theme_combo)
        layout.addLayout(theme_layout)
        
        # Outros configs podem ser adicionados aqui
        
        # Botões
        button_layout = QHBoxLayout()
        ok_button = QPushButton('OK')
        cancel_button = QPushButton('Cancelar')
        
        def save_settings():
            selected_theme = theme_combo.currentText().lower()
            self.change_theme(selected_theme)
            dialog.accept()
        
        ok_button.clicked.connect(save_settings)
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def show_about(self):
        """Mostra informações sobre o aplicativo."""
        QMessageBox.about(self, 'Sobre KutsakAI Web Agent Builder',
                          '<h3>KutsakAI Web Agent Builder v2.0</h3>'
                          '<p>Gerador de sites inteligente com IA.</p>'
                          '<p><b>Recursos:</b></p>'
                          '<ul>'
                          '<li>Geração automática de código HTML, CSS, JS</li>'
                          '<li>Editor avançado com preview em tempo real</li>'
                          '<li>Integração com modelos Ollama</li>'
                          '<li>Interface moderna e responsiva</li>'
                          '</ul>'
                          '<p><small>Desenvolvido com PyQt6 e Ollama</small></p>')
    
    def tray_icon_activated(self, reason):
        """Ação quando o ícone da bandeja é ativado."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def closeEvent(self, event):
        """Evento de fechamento da janela."""
        self.save_geometry()
        
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            reply = QMessageBox.question(
                self, 'Confirmar Saída',
                'Deseja realmente sair?\n\nO aplicativo continuará rodando na bandeja do sistema.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
                self.hide()
        else:
            event.accept()

def init_application():
    """Inicializa a aplicação com splash screen e carregamento."""
    app = QApplication(sys.argv)
    
    # Configurar ícone global
    icon_path = os.path.join(os.path.dirname(__file__), 'site_generator', 'assets', 'kutsakai_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Splash screen
    splash = SplashScreen()
    splash.show()
    
    # Simular carregamento
    splash.update_progress(20, 'Carregando configurações...')
    time.sleep(0.5)
    
    splash.update_progress(40, 'Inicializando interface...')
    time.sleep(0.3)
    
    splash.update_progress(60, 'Carregando componentes IA...')
    time.sleep(0.4)
    
    splash.update_progress(80, 'Preparando editor...')
    time.sleep(0.3)
    
    splash.update_progress(100, 'Pronto!')
    time.sleep(0.2)
    
    # Criar janela principal
    window = CoderAgentGUI()
    window.show()
    
    # Fechar splash
    splash.finish(window)
    
    return app, window

if __name__ == '__main__':
    app, window = init_application()
    sys.exit(app.exec())
