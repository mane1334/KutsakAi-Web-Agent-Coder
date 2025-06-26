"""
Gerenciador de memória e preferências do projeto.
Armazena e aprende com as preferências do usuário.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class ProjectMemory:
    def __init__(self):
        self.memory_file = os.path.join(os.path.dirname(__file__), 'project_memory.json')
        self.current_project = None
        self.memories = self.load_memories()
        
    def load_memories(self) -> dict:
        """Carrega as memórias salvas."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erro ao carregar memórias: {e}")
            return {}
            
    def save_memories(self):
        """Salva as memórias no arquivo."""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar memórias: {e}")
            
    def set_current_project(self, project_path: str):
        """Define o projeto atual."""
        self.current_project = project_path
        if project_path not in self.memories:
            self.memories[project_path] = {
                'preferences': {
                    'colors': [],
                    'fonts': [],
                    'style': '',
                    'layout': ''
                },
                'feedback': {
                    'liked': [],
                    'disliked': []
                },
                'history': [],
                'embeddings': {},
                'stats': {
                    'improvements': 0,
                    'positive_feedback': 0,
                    'negative_feedback': 0
                }
            }
            self.save_memories()
            
    def add_preference(self, category: str, value: Any):
        """Adiciona uma preferência ao projeto atual."""
        if not self.current_project:
            return
            
        prefs = self.memories[self.current_project]['preferences']
        if isinstance(prefs[category], list):
            if value not in prefs[category]:
                prefs[category].append(value)
        else:
            prefs[category] = value
        self.save_memories()
        
    def add_feedback(self, improvement: str, liked: bool):
        """Registra feedback do usuário sobre uma melhoria."""
        if not self.current_project:
            return
            
        feedback = self.memories[self.current_project]['feedback']
        target_list = feedback['liked'] if liked else feedback['disliked']
        
        if improvement not in target_list:
            target_list.append(improvement)
            
        # Atualizar estatísticas
        stats = self.memories[self.current_project]['stats']
        if liked:
            stats['positive_feedback'] += 1
        else:
            stats['negative_feedback'] += 1
            
        self.save_memories()
        
    def add_history_entry(self, action: str, details: dict):
        """Adiciona uma entrada ao histórico do projeto."""
        if not self.current_project:
            return
            
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        }
        
        self.memories[self.current_project]['history'].append(entry)
        self.save_memories()
        
    def get_project_style(self) -> Dict[str, Any]:
        """Retorna o estilo aprendido do projeto."""
        if not self.current_project:
            return {}
            
        return self.memories[self.current_project]['preferences']
        
    def get_successful_patterns(self) -> List[str]:
        """Retorna padrões que tiveram feedback positivo."""
        if not self.current_project:
            return []
            
        return self.memories[self.current_project]['feedback']['liked']
        
    def get_improvement_prompt(self, base_prompt: str) -> str:
        """Enriquece o prompt com contexto do projeto."""
        if not self.current_project:
            return base_prompt
            
        prefs = self.memories[self.current_project]['preferences']
        liked = self.memories[self.current_project]['feedback']['liked']
        
        # Construir prompt contextualizado
        context = []
        
        if prefs['style']:
            context.append(f"Manter o estilo: {prefs['style']}")
            
        if prefs['colors']:
            context.append(f"Usar as cores preferidas: {', '.join(prefs['colors'])}")
            
        if prefs['fonts']:
            context.append(f"Usar as fontes preferidas: {', '.join(prefs['fonts'])}")
            
        if liked:
            context.append(f"Incorporar elementos bem sucedidos como: {', '.join(liked[:3])}")
            
        if context:
            enhanced_prompt = f"{base_prompt}\n\nContexto do projeto:\n" + "\n".join(context)
            return enhanced_prompt
            
        return base_prompt
