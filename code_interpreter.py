# Execução e avaliação de código
import subprocess
import tempfile
import sys

def interpret_code(code):
    """
    Executa código Python de forma segura em um subprocesso e retorna a saída ou erro.
    """
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run([sys.executable, tmp_path], capture_output=True, text=True, timeout=10)
        output = result.stdout
        error = result.stderr
        if error:
            return f"[Erro]\n{error}"
        return output
    except Exception as e:
        return f"[Erro de execução: {e}]"
