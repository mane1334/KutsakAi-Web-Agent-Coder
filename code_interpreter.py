# Execução e avaliação de código
import subprocess
import tempfile
import sys

def interpret_code(code, sandbox=True):
    """
    Executa código Python de forma segura em um subprocesso.
    Se sandbox=True, aplica restrições adicionais.
    """
    # Adicionar restrições ao código se estiver em modo sandbox
    if sandbox:
        restricted_code = f"""
import sys
import os

# Restringir acesso a comandos perigosos
def restricted_exit(*args, **kwargs):
    print("[Sandbox] Tentativa de fechar o processo bloqueada.")

sys.exit = restricted_exit

# Remover módulos perigosos
dangerous_modules = ['shutil', 'os.path', 'subprocess']
for mod in dangerous_modules:
    if mod in sys.modules:
        del sys.modules[mod]

# Executar o código original
{code}
"""
    else:
        restricted_code = code

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as tmp:
        tmp.write(restricted_code)
        tmp_path = tmp.name
        
    try:
        # Usar um limite de memória e tempo
        # Nota: Em sistemas Linux reais, poderíamos usar 'ulimit' ou 'resource'
        result = subprocess.run(
            [sys.executable, tmp_path], 
            capture_output=True, 
            text=True, 
            timeout=10,
            env={"PYTHONPATH": os.getcwd()} # Manter contexto do projeto
        )
        
        output = result.stdout
        error = result.stderr
        
        if error:
            return f"[Erro]\n{error}"
        return output or "Código executado com sucesso (sem saída)."
    except subprocess.TimeoutExpired:
        return "[Erro] Tempo limite de execução (10s) excedido."
    except Exception as e:
        return f"[Erro de execução: {e}]"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
