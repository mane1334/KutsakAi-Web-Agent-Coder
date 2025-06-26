# Integração com Yarn/RAG
import json
import os

RAG_PATH = 'rag_store.json'

def store_text(text):
    """Guarda texto relevante para RAG."""
    textos = []
    if os.path.exists(RAG_PATH):
        with open(RAG_PATH, 'r', encoding='utf-8') as f:
            textos = json.load(f)
    textos.append(text)
    with open(RAG_PATH, 'w', encoding='utf-8') as f:
        json.dump(textos, f, ensure_ascii=False, indent=2)

def retrieve_relevant_text(query):
    """Recupera texto relevante baseado em busca simples."""
    if not os.path.exists(RAG_PATH):
        return ''
    with open(RAG_PATH, 'r', encoding='utf-8') as f:
        textos = json.load(f)
    # Busca simples: retorna o primeiro texto que contém a query
    for t in textos:
        if query.lower() in t.lower():
            return t
    return ''
