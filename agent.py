import argparse
from ollama_client import generate_code, list_models
from file_manager import create_file, update_file, remove_file_or_folder
from code_interpreter import interpret_code
from history import save_interaction, get_history
from web_search import search_code
from rag_yarn import store_text, retrieve_relevant_text

# CLI principal do agente coder

def main():
    parser = argparse.ArgumentParser(description='Agente Coder CLI')
    parser.add_argument('command', choices=['create', 'update', 'remove', 'run', 'search', 'self-improve', 'models', 'history', 'rag-store', 'rag-get'], help='Comando do agente')
    parser.add_argument('--target', help='Arquivo ou pasta alvo')
    parser.add_argument('--code', help='Código para interpretar ou corrigir')
    parser.add_argument('--query', help='Consulta para busca na web')
    parser.add_argument('--model', help='Nome do modelo Ollama a ser usado')
    args = parser.parse_args()

    if args.command == 'models':
        from config_manager import get_config
        active_provider = get_config("providers.active", "ollama")
        modelos = list_models()
        print(f'Modelos disponíveis no provedor ativo ({active_provider}):')
        for m in modelos:
            print(f'- {m}')
        return

    if args.command == 'create' and args.target and args.code:
        print(create_file(args.target, args.code))
        return

    if args.command == 'update' and args.target and args.code:
        print(update_file(args.target, args.code))
        return

    if args.command == 'remove' and args.target:
        print(remove_file_or_folder(args.target))
        return

    if args.command == 'run' and args.code:
        print('--- Saída da execução ---')
        print(interpret_code(args.code))
        return

    if args.command == 'search' and args.query:
        print('--- Resultado da busca web ---')
        print(search_code(args.query))
        return

    if args.command == 'history':
        print('--- Histórico de interações ---')
        for item in get_history():
            print(item)
        return

    if args.command == 'rag-store' and args.code:
        store_text(args.code)
        print('Texto armazenado no RAG.')
        return

    if args.command == 'rag-get' and args.query:
        print('--- Texto relevante do RAG ---')
        print(retrieve_relevant_text(args.query))
        return

    if args.command == 'self-improve':
        print('Função de auto-melhoria ainda não implementada.')
        return

    print('Comando ou argumentos inválidos.')

if __name__ == '__main__':
    main()
