# Gerenciamento de histórico de interações
import json
import os

HIST_PATH = 'history.json'

def save_interaction(data):
    historico = []
    if os.path.exists(HIST_PATH):
        with open(HIST_PATH, 'r', encoding='utf-8') as f:
            historico = json.load(f)
    historico.append(data)
    with open(HIST_PATH, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def get_history():
    if not os.path.exists(HIST_PATH):
        return []
    with open(HIST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
