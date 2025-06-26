
import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QComboBox, QMessageBox,
    QListWidget
)

class RAGDashboard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Dashboard de Exemplos RAG')
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(['html', 'css', 'js'])
        layout.addWidget(QLabel('Tipo de exemplo:'))
        layout.addWidget(self.tipo_combo)
        self.lista = QListWidget()
        layout.addWidget(QLabel('Exemplos salvos:'))
        layout.addWidget(self.lista)
        self.exemplo_edit = QTextEdit()
        self.exemplo_edit.setPlaceholderText('Cole aqui um exemplo de código para salvar...')
        layout.addWidget(QLabel('Novo exemplo:'))
        layout.addWidget(self.exemplo_edit)
        btns = QHBoxLayout()
        self.add_btn = QPushButton('Adicionar Exemplo')
        self.del_btn = QPushButton('Remover Selecionado')
        btns.addWidget(self.add_btn)
        btns.addWidget(self.del_btn)
        layout.addLayout(btns)
        self.add_btn.clicked.connect(self.add_exemplo)
        self.del_btn.clicked.connect(self.del_exemplo)
        self.tipo_combo.currentTextChanged.connect(self.load_lista)
        self.rag_path = os.path.join(os.path.dirname(__file__), '..', '..', 'rag_store.json')
        self.load_lista()

    def load_lista(self):
        self.lista.clear()
        tipo = self.tipo_combo.currentText()
        if not os.path.exists(self.rag_path):
            return
        try:
            with open(self.rag_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            for item in dados:
                if item.get('tipo') == tipo:
                    self.lista.addItem(item.get('exemplo', ''))
        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Erro ao ler rag_store.json: {e}')

    def add_exemplo(self):
        exemplo = self.exemplo_edit.toPlainText().strip()
        tipo = self.tipo_combo.currentText()
        if not exemplo:
            QMessageBox.warning(self, 'Aviso', 'Digite ou cole um exemplo!')
            return
        # Carrega dados existentes
        dados = []
        if os.path.exists(self.rag_path):
            try:
                with open(self.rag_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception:
                pass
        dados.append({'tipo': tipo, 'exemplo': exemplo})
        try:
            with open(self.rag_path, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            self.exemplo_edit.clear()
            self.load_lista()
        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Erro ao salvar: {e}')

    def del_exemplo(self):
        idx = self.lista.currentRow()
        if idx < 0:
            QMessageBox.warning(self, 'Aviso', 'Selecione um exemplo para remover!')
            return
        tipo = self.tipo_combo.currentText()
        # Carrega dados existentes
        dados = []
        if os.path.exists(self.rag_path):
            try:
                with open(self.rag_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception:
                pass
        # Remove o exemplo selecionado desse tipo
        exemplos_tipo = [i for i in dados if i.get('tipo') == tipo]
        if idx < len(exemplos_tipo):
            exemplo_remover = exemplos_tipo[idx]['exemplo']
            dados = [i for i in dados if not (i.get('tipo') == tipo and i.get('exemplo') == exemplo_remover)]
            try:
                with open(self.rag_path, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
                self.load_lista()
            except Exception as e:
                QMessageBox.warning(self, 'Erro', f'Erro ao remover: {e}')
