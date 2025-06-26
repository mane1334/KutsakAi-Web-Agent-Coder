# Proposta de Reorganização da UI - Aba Editor

## Estrutura Atual
- **Layout Horizontal**: File Tree | Editor Tabs + Bottom Panel | Preview
- **Bottom Panel**: Git, Problems, Snippets, AI Tools
- **Toolbar**: Básico com Open Project, Save All

## Problemas Identificados
1. **Espaço vertical limitado** para o editor devido ao painel inferior
2. **AI Tools** não estão em destaque suficiente
3. **Preview** está sempre visível, ocupando espaço
4. **Toolbar** muito simples, sem acesso rápido a funcionalidades importantes
5. **File Tree** pode ser colapsável para mais espaço
6. **Snippets** poderiam ter melhor organização

## Nova Proposta de Layout

### 1. Barra Superior Modernizada
```
[🏠 Home] [📂 Open] [💾 Save] [💾 Save All] | [🔄 Refresh] [🌐 Preview Toggle] | [🤖 AI Assistant] [⚙️ Settings]
```

### 2. Layout Principal com Painéis Colapsáveis
```
┌─[File Explorer]─┬─────[Editor Principal]─────┬─[AI Assistant]─┐
│ 📁 Project      │ ┌─[Tab1]─[Tab2]─[Tab+]─┐  │ 🤖 AI Tools    │
│ ├─ index.html   │ │                        │  │ ┌─────────────┐ │
│ ├─ styles.css   │ │    EDITOR AREA         │  │ │ Quick AI    │ │
│ ├─ script.js    │ │                        │  │ │ Improve     │ │
│ └─ assets/      │ │                        │  │ └─────────────┘ │
│                 │ └────────────────────────┘  │ Model: [▼]      │
│ [🔍 Search]     │                             │ Prompt: [____]  │
│ [+ New File]    │ ┌─[Problems]─[Output]─┐    │ [✨ Improve]    │
│                 │ │ ○ No errors found   │    │ [🔁 Loop 5x]    │
│                 │ └─────────────────────┘    │                 │
└─────────────────┴─────────────────────────────┴─────────────────┘
```

### 3. Painel de Preview Sobreposto/Modal
- Preview como **overlay modal** ou **painel deslizante lateral**
- Ativado por botão ou tecla de atalho (F12)
- Múltiplos tamanhos de preview (Desktop, Tablet, Mobile)
- Preview em tempo real opcional

### 4. AI Assistant Panel Lateral
- **Fixo no lado direito** ou **colapsável**
- Quick actions sempre visíveis
- Histórico de melhorias
- Templates e snippets inteligentes

## Implementação da Nova UI

### Estrutura de Componentes:

1. **ModernToolbar** - Barra superior com ações rápidas
2. **SidebarFileExplorer** - Explorador colapsável
3. **CentralEditorArea** - Área principal do editor
4. **AIAssistantPanel** - Painel de IA lateral
5. **BottomStatusPanel** - Painel inferior minimalista
6. **OverlayPreview** - Preview sobreposto

### Benefícios da Nova Organização:

✅ **Mais espaço vertical** para o código
✅ **AI tools sempre acessíveis** sem ocupar espaço do editor
✅ **Preview on-demand** para não distrair
✅ **File explorer colapsável** para projetos grandes
✅ **Quick actions** na toolbar
✅ **Melhor fluxo de trabalho** para desenvolvimento com IA

### Funcionalidades Adicionadas:

1. **Quick AI Improve** - Botão de melhoria rápida
2. **Smart Snippets** - Snippets contextuais baseados no arquivo
3. **Live Preview Toggle** - Preview em tempo real opcional
4. **Project Templates** - Templates rápidos para novos arquivos
5. **Code Stats** - Estatísticas do projeto (linhas, arquivos, etc.)
6. **Recent Files** - Acesso rápido a arquivos recentes
7. **Breadcrumbs** - Navegação por estrutura de pastas
8. **Split Editor** - Editor dividido para comparação

### Layout Responsivo:

- **Tela grande**: Todos os painéis visíveis
- **Tela média**: AI Panel colapsado, File Explorer menor
- **Tela pequena**: Painéis como tabs/modals

### Teclas de Atalho:

- `Ctrl+Shift+P` - Command Palette
- `F12` - Toggle Preview
- `Ctrl+Shift+A` - AI Assistant
- `Ctrl+B` - Toggle File Explorer
- `Ctrl+Shift+F` - Find in Files
- `Ctrl+Shift+I` - AI Improve
