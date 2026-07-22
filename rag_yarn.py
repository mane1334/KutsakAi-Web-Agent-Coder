import json
import os
import math
from typing import List, Dict, Any
from collections import Counter

RAG_PATH = 'rag_store.json'

def tokenize(text: str) -> List[str]:
    """Tokenização simples para busca semântica."""
    return text.lower().split()

def compute_tfidf(text: str, corpus: List[str]) -> Dict[str, float]:
    """Calcula TF-IDF simplificado para um texto."""
    tokens = tokenize(text)
    tf = Counter(tokens)
    num_tokens = len(tokens)
    
    tfidf = {}
    for token, count in tf.items():
        # TF
        tf_val = count / num_tokens
        # IDF (simplificado)
        docs_with_token = sum(1 for d in corpus if token in d.lower())
        idf_val = math.log(len(corpus) / (1 + docs_with_token))
        tfidf[token] = tf_val * idf_val
    return tfidf

def cosine_similarity(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    """Calcula a similaridade de cosseno entre dois vetores esparsos."""
    sum_xx, sum_yy, sum_xy = 0, 0, 0
    for r in v1:
        sum_xx += v1[r] * v1[r]
        if r in v2:
            sum_xy += v1[r] * v2[r]
    for r in v2:
        sum_yy += v2[r] * v2[r]
    
    denominator = math.sqrt(sum_xx) * math.sqrt(sum_yy)
    if not denominator:
        return 0.0
    return sum_xy / denominator

def store_text(text: str, metadata: Dict[str, Any] = None):
    """Guarda texto relevante para RAG com metadados."""
    entries = []
    if os.path.exists(RAG_PATH):
        try:
            with open(RAG_PATH, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        except:
            entries = []
            
    entry = {
        "text": text,
        "metadata": metadata or {},
        "timestamp": os.path.getmtime(RAG_PATH) if os.path.exists(RAG_PATH) else 0
    }
    entries.append(entry)
    
    with open(RAG_PATH, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def retrieve_relevant_text(query: str, top_k: int = 3) -> str:
    """Recupera texto relevante usando busca semântica (TF-IDF + Cosseno)."""
    if not os.path.exists(RAG_PATH):
        return ''
        
    try:
        with open(RAG_PATH, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except:
        return ''
        
    if not entries:
        return ''
        
    corpus = [e['text'] for e in entries]
    query_vector = compute_tfidf(query, corpus)
    
    scored_entries = []
    for entry in entries:
        entry_vector = compute_tfidf(entry['text'], corpus)
        score = cosine_similarity(query_vector, entry_vector)
        scored_entries.append((score, entry['text']))
    
    # Ordenar por score descendente
    scored_entries.sort(key=lambda x: x[0], reverse=True)
    
    # Retornar os top_k resultados combinados
    results = [text for score, text in scored_entries[:top_k] if score > 0]
    return "\n---\n".join(results) if results else ''
