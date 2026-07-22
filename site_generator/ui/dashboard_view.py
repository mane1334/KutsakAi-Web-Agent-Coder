from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
    QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import datetime

from logger import StructuredLogger
from cache_system import get_cache

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = StructuredLogger()
        self.cache = get_cache()
        self.setup_ui()
        
        # Timer para atualização automática
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(2000)  # Atualiza a cada 2 segundos

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("📊 Dashboard de Observabilidade")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #6366f1; margin-bottom: 10px;")
        main_layout.addWidget(header)

        # Scroll Area para o conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(20)
        
        # Grid para métricas rápidas
        self.setup_metrics_grid()
        
        # Seção de Cache
        self.setup_cache_section()
        
        # Seção de Performance
        self.setup_performance_section()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def setup_metrics_grid(self):
        grid_frame = QFrame()
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(15)

        self.cards = {}
        metrics = [
            ("Total de Eventos", "0", "events"),
            ("Taxa de Acerto Cache", "0%", "cache_hit"),
            ("Tempo Médio Resposta", "0ms", "avg_time"),
            ("Erros Detectados", "0", "errors")
        ]

        for i, (title, value, key) in enumerate(metrics):
            card = self.create_metric_card(title, value)
            grid_layout.addWidget(card, i // 2, i % 2)
            self.cards[key] = card

        self.content_layout.addWidget(grid_frame)

    def create_metric_card(self, title, value):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #999; font-size: 12px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #fff; font-size: 24px; font-weight: bold;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Guardar referência para o label de valor
        card.value_label = value_label
        return card

    def setup_cache_section(self):
        section = QFrame()
        section.setStyleSheet("background: #1a1a1a; border-radius: 12px; padding: 15px;")
        layout = QVBoxLayout(section)
        
        title = QLabel("💾 Estado do Cache")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.cache_progress = QProgressBar()
        self.cache_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2a2a2a;
                border-radius: 5px;
                text-align: center;
                height: 20px;
                color: #fff;
            }
            QProgressBar::chunk {
                background-color: #6366f1;
            }
        """)
        layout.addWidget(self.cache_progress)
        
        self.cache_details = QLabel("Entradas: 0 | Tamanho: 0 MB")
        self.cache_details.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(self.cache_details)
        
        self.content_layout.addWidget(section)

    def setup_performance_section(self):
        section = QFrame()
        section.setStyleSheet("background: #1a1a1a; border-radius: 12px; padding: 15px;")
        layout = QVBoxLayout(section)
        
        title = QLabel("⚡ Performance das Funções")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.perf_list = QLabel("Nenhuma métrica disponível")
        self.perf_list.setStyleSheet("color: #e6e6e6; font-family: 'Consolas'; font-size: 11px;")
        self.perf_list.setWordWrap(True)
        layout.addWidget(self.perf_list)
        
        self.content_layout.addWidget(section)

    def refresh_stats(self):
        # Atualizar Cache
        stats = self.cache.get_statistics()
        mem = self.cache.get_memory_usage()
        
        hit_rate = stats.get('hit_rate', 0) * 100
        self.cards['cache_hit'].value_label.setText(f"{hit_rate:.1f}%")
        
        total_entries = stats.get('total_entries', 0)
        max_entries = mem.get('max_entries', 100)
        self.cache_progress.setValue(int((total_entries / max_entries) * 100) if max_entries > 0 else 0)
        
        db_size = mem.get('database_size_mb', 0)
        self.cache_details.setText(f"Entradas: {total_entries} | Tamanho DB: {db_size:.2f} MB")

        # Atualizar Performance
        all_perf = self.logger.performance_monitor.get_all_statistics()
        perf_text = ""
        total_time = 0
        count = 0
        
        for func, p_stats in all_perf.items():
            avg = p_stats.get('avg_time', 0) * 1000 # converter para ms
            perf_text += f"• {func}: {avg:.1f}ms (x{p_stats.get('count', 0)})\n"
            total_time += avg
            count += 1
            
        if perf_text:
            self.perf_list.setText(perf_text)
            avg_total = total_time / count if count > 0 else 0
            self.cards['avg_time'].value_label.setText(f"{avg_total:.1f}ms")
        
        # Atualizar Eventos e Erros
        events_count = len(self.logger.events_buffer)
        self.cards['events'].value_label.setText(str(events_count))
        
        errors = sum(1 for e in self.logger.events_buffer if e.get('level') == 'error')
        self.cards['errors'].value_label.setText(str(errors))
        if errors > 0:
            self.cards['errors'].setStyleSheet("QFrame { background: #1a1a1a; border: 1px solid #ef4444; border-radius: 12px; padding: 15px; }")
        else:
            self.cards['errors'].setStyleSheet("QFrame { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; padding: 15px; }")
