"""
Gerenciador de histórico de código e melhorias.
Mantém registro das gerações e melhorias feitas pela IA para aprendizado contínuo.
"""

import json
import os
import time
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CodeGeneration:
    """Representa uma geração ou melhoria de código."""
    file_path: str
    original_content: str
    improved_content: str
    prompt: str
    model: str
    timestamp: float
    success_rating: Optional[float] = None  # Rating dado pelo usuário (0-1)
    tokens_used: Optional[int] = None
    execution_time: Optional[float] = None
    context_files: List[str] = None  # Arquivos usados como contexto

class CodeHistoryManager:
    def __init__(self, history_file: str = "code_generations.json"):
        """
        Inicializa o gerenciador de histórico.
        
        Args:
            history_file: Caminho para o arquivo de histórico JSON
        """
        self.history_file = history_file
        self.history: Dict[str, List[CodeGeneration]] = {}
        self.load_history()
        
    def load_history(self):
        """Carrega o histórico do arquivo JSON."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for file_path, generations in data.items():
                        self.history[file_path] = [
                            CodeGeneration(**gen) for gen in generations
                        ]
                    logger.info(f"Histórico carregado com {len(self.history)} arquivos")
        except Exception as e:
            logger.error(f"Erro ao carregar histórico: {e}")
            self.history = {}
            
    def save_history(self):
        """Salva o histórico no arquivo JSON."""
        try:
            # Converter dataclasses para dicionários
            serializable = {
                path: [asdict(gen) for gen in generations]
                for path, generations in self.history.items()
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
            logger.info("Histórico salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")
            
    def add_generation(self, generation: CodeGeneration):
        """
        Adiciona uma nova geração ao histórico.
        
        Args:
            generation: Objeto CodeGeneration com os detalhes da geração
        """
        if generation.file_path not in self.history:
            self.history[generation.file_path] = []
        
        self.history[generation.file_path].append(generation)
        self.save_history()
        
    def get_file_history(self, file_path: str) -> List[CodeGeneration]:
        """
        Retorna o histórico de gerações para um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Lista de gerações ordenada por timestamp
        """
        return sorted(
            self.history.get(file_path, []),
            key=lambda x: x.timestamp
        )
        
    def get_successful_patterns(self, min_rating: float = 0.8) -> List[Dict]:
        """
        Identifica padrões de código bem sucedidos baseado no rating.
        
        Args:
            min_rating: Rating mínimo para considerar sucesso (0-1)
            
        Returns:
            Lista de padrões bem sucedidos com seus contextos
        """
        patterns = []
        for generations in self.history.values():
            for gen in generations:
                if gen.success_rating and gen.success_rating >= min_rating:
                    patterns.append({
                        'prompt': gen.prompt,
                        'improvement': gen.improved_content,
                        'context_files': gen.context_files,
                        'rating': gen.success_rating
                    })
        return patterns
        
    def analyze_improvements(self, file_path: str) -> Dict:
        """
        Analisa as melhorias feitas em um arquivo ao longo do tempo.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com métricas e análises das melhorias
        """
        generations = self.get_file_history(file_path)
        if not generations:
            return {}
            
        return {
            'total_generations': len(generations),
            'avg_rating': sum(g.success_rating or 0 for g in generations) / len(generations),
            'last_improved': generations[-1].timestamp,
            'total_tokens': sum(g.tokens_used or 0 for g in generations),
            'avg_execution_time': sum(g.execution_time or 0 for g in generations) / len(generations)
        }
        
    def suggest_improvements(self, file_path: str, content: str) -> Optional[str]:
        """
        Sugere melhorias baseado no histórico de sucessos anteriores.
        
        Args:
            file_path: Caminho do arquivo
            content: Conteúdo atual do arquivo
            
        Returns:
            Prompt sugerido para melhoria ou None
        """
        patterns = self.get_successful_patterns()
        if not patterns:
            return None
            
        # TODO: Implementar lógica de matching de padrões
        # Por enquanto retorna o padrão mais bem avaliado
        best_pattern = max(patterns, key=lambda x: x['rating'])
        return f"Melhore este código seguindo o padrão:\n{best_pattern['improvement']}"
        
    def cleanup_old_entries(self, days: int = 30):
        """
        Remove entradas antigas do histórico.
        
        Args:
            days: Número de dias para manter no histórico
        """
        cutoff = time.time() - (days * 24 * 60 * 60)
        for file_path in list(self.history.keys()):
            self.history[file_path] = [
                gen for gen in self.history[file_path]
                if gen.timestamp > cutoff
            ]
            if not self.history[file_path]:
                del self.history[file_path]
        self.save_history()
