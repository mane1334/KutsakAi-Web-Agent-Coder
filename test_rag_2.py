from rag_yarn import store_text, retrieve_relevant_text
import os

# Limpar store anterior para o teste
if os.path.exists('rag_store.json'):
    os.remove('rag_store.json')

print("Testando RAG 2.0 (Busca Semântica TF-IDF)...")

# Guardar alguns snippets
store_text("Como fazer um botão azul com TailwindCSS: <button class='bg-blue-500 text-white'>Clique aqui</button>", {"type": "ui"})
store_text("Configuração de conexão com banco de dados MySQL usando SQLAlchemy.", {"type": "backend"})
store_text("Lógica de autenticação JWT para proteger rotas da API.", {"type": "security"})

# Testar busca semântica (palavras relacionadas mas não idênticas)
query = "criar componente de interface azul"
print(f"\nQuery: '{query}'")
result = retrieve_relevant_text(query)
print(f"Resultado:\n{result}")

query = "proteger rotas com token"
print(f"\nQuery: '{query}'")
result = retrieve_relevant_text(query)
print(f"Resultado:\n{result}")

print("\nTeste concluído!")
