# 🚀 KutsakAI Coder Agent

Agente de programação IA local avançado, inspirado no Claude Code, usando Ollama e PyQt6. Uma ferramenta completa para desenvolvimento web moderno com interface gráfica intuitiva.

## 🌟 Funcionalidades

### 🤖 IA e Automação
- **Multi-Provedor LLM**: Suporte para **Ollama, OpenRouter e NVIDIA**.
- **RAG 2.0 (Memória Semântica)**: Sistema avançado de recuperação de contexto usando TF-IDF e Similaridade de Cosseno para entender o seu código.
- **Interpretador de Código Seguro (Sandbox)**: Execução de código Python com restrições de segurança para proteger o seu sistema.
- **Geração inteligente de código** com contexto de projeto enriquecido.
- **Correção automática de bugs** e otimização.
- **Busca de código na web** integrada.

### 🎨 Interface Gráfica (PyQt6)
- **Dashboard de Observabilidade**: Visualize em tempo real a performance, uso de cache, eventos e erros do sistema.
- **Visualização de Diff**: Revise as alterações propostas pela IA antes de as aplicar ao seu código.
- **Interface UI/UX Moderna**: Design profissional com foco em produtividade.
- **Seletor de Provedores e Modelos** em todas as abas principais.
- **Diálogo de Configurações** para chaves de API.
- **Editor de código** avançado com syntax highlighting.
- **Chat com IA** interativo com suporte a streaming.
- **Preview em tempo real** de projetos web.

### 📁 Gerenciamento de Arquivos
- **Manipulação de arquivos e pastas**
- **Sistema de histórico** de interações
- **Gerenciamento de projetos** web
- **Sistema de cache** otimizado

### 🌐 Desenvolvimento Web
- **Novos Skills de Design**: Suporte para **DaisyUI, Flowbite e Chakra UI**.
- **Novos Tipos de Site**: Landing Pages Modernas, SaaS, Portfólios Minimalistas, E-commerce, etc.
- **Suporte completo ao TailwindCSS**.
- **Templates inteligentes** e reutilizáveis.
- **Responsividade mobile-first**.
- **Acessibilidade WCAG 2.1 AA**.
- **Preview fullscreen** de projetos.

## 📋 Pré-requisitos

- **Python 3.8+** (recomendado 3.11+)
- **Ollama** instalado e rodando localmente
- **Node.js 18+** (para dependências frontend)
- **Git** (opcional, para controle de versão)

## 🛠️ Instalação

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/coder_agent.git
cd coder_agent
```

### 2. Instalar dependências Python
```bash
pip install -r requirements.txt
```

### 3. Instalar dependências Node.js
```bash
npm install
```

### 4. Configurar Ollama
```bash
# Instalar modelo recomendado
ollama pull codellama

# Ou usar outro modelo de sua preferência
ollama pull llama2
```

## 🚀 Uso

### Interface Gráfica (Recomendado)
```bash
python gui.py
```

### CLI (Linha de Comando)
```bash
python agent.py [comando] [opções]
```

#### Comandos CLI Disponíveis:

```bash
# Listar modelos disponíveis
python agent.py models

# Criar arquivo
python agent.py create --target "exemplo.py" --code "print('Hello World')"

# Atualizar arquivo
python agent.py update --target "exemplo.py" --code "print('Hello Updated')"

# Remover arquivo/pasta
python agent.py remove --target "exemplo.py"

# Executar código
python agent.py run --code "print('Executando...')"

# Buscar na web
python agent.py search --query "Python best practices"

# Ver histórico
python agent.py history

# Armazenar no RAG
python agent.py rag-store --code "Informação importante"

# Recuperar do RAG
python agent.py rag-get --query "informação"
```

## 📁 Estrutura do Projeto

```
coder_agent/
├── 📁 site_generator/          # Módulo gerador de sites
│   ├── 📁 ui/                 # Componentes da interface
│   │   ├── 📁 components/     # Componentes reutilizáveis
│   │   ├── 📁 panels/         # Painéis da aplicação
│   │   └── 📁 dialogs/        # Diálogos e modais
│   └── 📁 logic/              # Lógica de negócio
├── 📁 tests/                  # Testes automatizados
├── 📁 node_modules/           # Dependências Node.js
├── 🐍 agent.py               # CLI principal
├── 🖥️ gui.py                 # Interface gráfica
├── 🤖 ollama_client.py       # Cliente Ollama
├── 📁 file_manager.py        # Gerenciador de arquivos
├── ⚡ code_interpreter.py    # Interpretador de código
├── 📚 history.py             # Sistema de histórico
├── 🌐 web_search.py          # Busca web
├── 🧠 rag_yarn.py            # Sistema RAG
├── ⚙️ config_manager.py      # Configurações
├── 📊 logger.py              # Sistema de logs
├── 💾 cache_system.py        # Sistema de cache
├── 📦 requirements.txt       # Dependências Python
├── 📦 package.json           # Dependências Node.js
└── 📖 README.md              # Este arquivo
```

## ⚙️ Configuração

O projeto usa um sistema de configuração flexível através do `config_manager.py`. As principais configurações incluem:

- **URL do Ollama**: `http://localhost:11434` (padrão)
- **Modelo padrão**: `codellama`
- **Tema da interface**: dark/light
- **Configurações de cache**: habilitado por padrão

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=.

# Testes específicos
pytest tests/test_ollama_client.py
```

## 🤝 Contribuição

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

### 📋 Guidelines de Contribuição

- Siga o padrão **PEP 8** para Python
- Adicione **testes** para novas funcionalidades
- Mantenha a **documentação** atualizada
- Use **commits semânticos** (feat, fix, docs, etc.)

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🔗 Links Úteis

- [Ollama Documentation](https://ollama.ai/)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

## 📞 Suporte

Se você encontrar algum problema ou tiver sugestões:

1. Verifique os **issues** existentes
2. Crie um **novo issue** com detalhes

---

**Desenvolvido com ❤️ por [Manuel Pereira]**
