import sys
import os

# Adicionar o diretório atual ao sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

try:
    print("Testando sintaxe de llm_providers.py...")
    import llm_providers
    print("OK")
    
    print("Testando sintaxe de ollama_client.py...")
    import ollama_client
    print("OK")
    
    print("Testando sintaxe de config_manager.py...")
    import config_manager
    print("OK")
    
    print("Testando sintaxe de site_generator/chat_gui.py...")
    # Mocking PyQt6 to test logic without a display
    from unittest.mock import MagicMock
    sys.modules['PyQt6'] = MagicMock()
    sys.modules['PyQt6.QtWidgets'] = MagicMock()
    sys.modules['PyQt6.QtCore'] = MagicMock()
    sys.modules['PyQt6.QtGui'] = MagicMock()
    
    import site_generator.chat_gui
    print("OK")
    
    print("Todos os testes de sintaxe básicos passaram!")
except Exception as e:
    print(f"Erro detectado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
