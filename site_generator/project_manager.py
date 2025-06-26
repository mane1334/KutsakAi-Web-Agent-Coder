"""
Gerenciador de projetos de sites.
"""
import os
import shutil

class ProjectManager:
    def __init__(self):
        self.current_project = None
        
    def create_project(self, base_path, project_name):
        """Cria a estrutura base do projeto."""
        project_path = os.path.join(base_path, project_name)
        
        # Criar estrutura de pastas
        folders = ['css', 'js', 'img', 'assets']
        os.makedirs(project_path, exist_ok=True)
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
            
        self.current_project = project_path
        return project_path
        
    def save_files(self, html_content, css_content, js_content):
        """Salva os arquivos do projeto."""
        if not self.current_project:
            raise ValueError("Nenhum projeto aberto")
            
        # Salvar HTML
        with open(os.path.join(self.current_project, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        # Salvar CSS
        with open(os.path.join(self.current_project, 'css', 'styles.css'), 'w', encoding='utf-8') as f:
            f.write(css_content)
            
        # Salvar JavaScript
        with open(os.path.join(self.current_project, 'js', 'main.js'), 'w', encoding='utf-8') as f:
            f.write(js_content)
            
    def load_project(self, project_path):
        """Carrega um projeto existente."""
        if not os.path.exists(project_path):
            raise ValueError("Projeto não encontrado")
            
        self.current_project = project_path
        
        # Carregar arquivos
        files = {
            'html': os.path.join(project_path, 'index.html'),
            'css': os.path.join(project_path, 'css', 'styles.css'),
            'js': os.path.join(project_path, 'js', 'main.js')
        }
        
        contents = {}
        for file_type, file_path in files.items():
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    contents[file_type] = f.read()
            else:
                contents[file_type] = ''
                
        return contents
        
    def create_readme(self, project_description):
        """Cria arquivo README.md no projeto."""
        if not self.current_project:
            raise ValueError("Nenhum projeto aberto")
            
        readme_content = f"""# {os.path.basename(self.current_project)}

{project_description}

## Estrutura
- index.html - Página principal
- css/styles.css - Estilos do site
- js/main.js - Funcionalidades JavaScript
- img/ - Pasta para imagens
- assets/ - Outros recursos

## Como usar
1. Abra o arquivo index.html no navegador
2. As imagens podem ser adicionadas na pasta img/
3. Outros recursos podem ser colocados em assets/
"""
        
        with open(os.path.join(self.current_project, 'README.md'), 'w', encoding='utf-8') as f:
            f.write(readme_content)
