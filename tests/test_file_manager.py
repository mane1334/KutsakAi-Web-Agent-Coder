import os
import pytest
from file_manager import create_file, remove_file_or_folder

def test_create_and_remove_file(tmp_path):
    file_path = tmp_path / 'testfile.txt'
    content = 'conteúdo de teste'
    # Cria arquivo
    result = create_file(str(file_path), content)
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        assert f.read() == content
    # Remove arquivo
    result_remove = remove_file_or_folder(str(file_path))
    assert not os.path.exists(file_path) 