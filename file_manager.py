# Gerenciamento de arquivos e pastas
import os
import shutil

def create_file(path, content):
    dirname = os.path.dirname(path)
    if dirname:  # Só cria diretório se não for string vazia
        os.makedirs(dirname, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'Arquivo criado: {path}'

def update_file(path, content):
    if not os.path.exists(path):
        return f'Arquivo não existe: {path}'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'Arquivo atualizado: {path}'

def remove_file_or_folder(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        return f'Pasta removida: {path}'
    elif os.path.isfile(path):
        os.remove(path)
        return f'Arquivo removido: {path}'
    else:
        return f'Arquivo ou pasta não existe: {path}'
