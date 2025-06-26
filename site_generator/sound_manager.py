"""
Gerenciador de sons para notificações.
"""
import os
import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_default_sounds()
        
    def load_default_sounds(self):
        """Carrega os sons padrão."""
        try:
            sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
            done_sound = os.path.join(sounds_dir, 'done.mp3')
            
            if os.path.exists(done_sound):
                self.load_sound('done', done_sound)
            else:
                print(f"Arquivo de som não encontrado: {done_sound}")
        except Exception as e:
            print(f"Erro ao carregar sons padrão: {e}")
            
    def load_sound(self, name, path):
        """Carrega um arquivo de som."""
        try:
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
                print(f"Som '{name}' carregado com sucesso de {path}")
            else:
                print(f"Arquivo de som não encontrado: {path}")
        except Exception as e:
            print(f"Erro ao carregar som {name}: {e}")
            
    def play(self, name):
        """Toca um som carregado."""
        try:
            if name in self.sounds:
                self.sounds[name].play()
                print(f"Som '{name}' tocado com sucesso")
            else:
                print(f"Som '{name}' não encontrado no gerenciador")
        except Exception as e:
            print(f"Erro ao tocar som {name}: {e}")
                
sound_manager = SoundManager()
