from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCompleter, QToolTip
from PyQt6.QtGui import QFont, QColor, QPainter, QKeySequence, QTextCursor, QTextFormat
from PyQt6.QtCore import Qt, QRect, QSize, QEvent
from PyQt6.QtGui import QTextDocument, QShortcut
from PyQt6.QtWidgets import QAbstractScrollArea

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    def sizeHint(self):
        return QSize(self.line_number_width(), 0)
    def line_number_width(self):
        digits = len(str(max(1, self.editor.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor('#23272e'))
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor('#6a9955'))
                painter.drawText(0, top, self.width()-2, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
                # Linha de grade
                painter.setPen(QColor('#333'))
                painter.drawLine(self.width()-2, top, self.width()-2, bottom)
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_number += 1

class VSCTextEdit(QPlainTextEdit):
    def __init__(self, doc_keywords):
        super().__init__()
        self.doc_keywords = doc_keywords
        self.setFont(QFont('Consolas', 12))
        # Temas claro/escuro
        self.theme = 'dark'
        self.dark_qss = """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                padding: 10px;
            }
        """
        self.light_qss = """
            QTextEdit {
                background-color: #f5f5f5;
                color: #222;
                border: none;
                padding: 10px;
            }
        """
        self.setStyleSheet(self.dark_qss)
        QShortcut(QKeySequence('Ctrl+Alt+L'), self, activated=self.toggle_theme)
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        # Minimapa
        self.minimap = QTextEdit(self)
        self.minimap.setReadOnly(True)
        self.minimap.setFont(QFont('Consolas', 4))
        self.minimap.setStyleSheet("background: #23272e; color: #888; border: none;")
        self.minimap.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.minimap.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.minimap.setFixedWidth(80)
        self.minimap.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Múltiplos cursores: Ctrl+D
        QShortcut(QKeySequence('Ctrl+D'), self, activated=self.select_next_occurrence)
        self.textChanged.connect(self.update_minimap)
        self.verticalScrollBar().valueChanged.connect(self.sync_minimap_scroll)
        self.update_minimap()
        # Barra de busca incremental e substituição
        self.search_bar = QWidget(self)
        self.search_bar.setStyleSheet("background: #23272e; border-radius: 4px; padding: 4px;")
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(4, 2, 4, 2)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Buscar...')
        self.search_input.setStyleSheet("background: #1e1e1e; color: #d4d4d4; border: 1px solid #444; border-radius: 3px; padding: 2px 6px;")
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText('Substituir...')
        self.replace_input.setStyleSheet("background: #1e1e1e; color: #d4d4d4; border: 1px solid #444; border-radius: 3px; padding: 2px 6px;")
        self.next_btn = QPushButton('↓')
        self.prev_btn = QPushButton('↑')
        self.replace_btn = QPushButton('Substituir')
        self.replace_all_btn = QPushButton('Substituir Tudo')
        for btn in [self.next_btn, self.prev_btn, self.replace_btn, self.replace_all_btn]:
            btn.setStyleSheet("background: #007acc; color: white; border-radius: 3px; padding: 2px 8px;")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.replace_input)
        search_layout.addWidget(self.prev_btn)
        search_layout.addWidget(self.next_btn)
        search_layout.addWidget(self.replace_btn)
        search_layout.addWidget(self.replace_all_btn)
        self.search_bar.setVisible(False)
        self.search_input.textChanged.connect(self.incremental_search)
        self.next_btn.clicked.connect(lambda: self.incremental_search(forward=True))
        self.prev_btn.clicked.connect(lambda: self.incremental_search(forward=False))
        self.replace_btn.clicked.connect(self.replace_one)
        self.replace_all_btn.clicked.connect(self.replace_all)
        # Atalho Ctrl+F para abrir/fechar barra de busca
        QShortcut(QKeySequence('Ctrl+F'), self, activated=self.toggle_search_bar)
        # Atalhos de teclado customizáveis
        self.shortcuts = {
            'save': ('Ctrl+S', self.save_file),
            'find': ('Ctrl+F', self.toggle_search_bar),
            'comment': ('Ctrl+/', self.toggle_comment),
            'theme': ('Ctrl+Alt+L', self.toggle_theme),
        }
        self.shortcut_objs = []
        self.setup_shortcuts()
        self.textChanged.connect(self.run_linting)
        # Auto-complete básico
        self.keywords = [
            # HTML
            'html', 'head', 'body', 'div', 'span', 'script', 'style', 'link', 'meta', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'label', 'select', 'option', 'textarea',
            # CSS
            'color', 'background', 'margin', 'padding', 'border', 'display', 'flex', 'grid', 'font-size', 'font-family', 'width', 'height', 'position', 'absolute', 'relative', 'fixed', 'float', 'clear', 'overflow', 'z-index', 'align-items', 'justify-content',
            # JS
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return', 'document', 'window', 'addEventListener', 'querySelector', 'getElementById', 'console', 'log', 'alert', 'setTimeout', 'setInterval', 'class', 'constructor', 'this', 'new', 'import', 'export'
        ]
        self.completer = QCompleter(self.keywords + self.get_document_words(), self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)
        # Snippets básicos
        self.snippets = {
            'html:5': '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="UTF-8">\n    <title>Título</title>\n</head>\n<body>\n    $0\n</body>\n</html>',
            'for': 'for (let i = 0; i < N; i++) {\n    $0\n}',
            'func': 'function nome() {\n    $0\n}',
            'div': '<div>$0</div>',
        }
        QShortcut(QKeySequence('Tab'), self, activated=self.expand_snippet)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        if word in self.doc_keywords:
            QToolTip.showText(event.globalPos(), self.doc_keywords[word], self)
        else:
            QToolTip.hideText()

    def expand_snippet(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        if word in self.snippets:
            snippet = self.snippets[word]
            cursor.insertText(snippet.replace('$0', ''))

    def setup_shortcuts(self):
        for name, (seq, func) in self.shortcuts.items():
            sc = QShortcut(QKeySequence(seq), self, activated=func)
            self.shortcut_objs.append(sc)

    def save_file(self):
        # Salva o arquivo atual (se integrado ao sistema de abas)
        if hasattr(self.parent(), 'file_path'):
            with open(self.parent().file_path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())

    def toggle_comment(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        # Detecta linguagem pelo conteúdo
        text = self.toPlainText()
        if '<html' in text or '<div' in text:
            comment_str = '<!--'
            end_comment_str = '-->'
            is_html = True
        elif '{' in text or 'function' in text:
            comment_str = '//'
            end_comment_str = ''
            is_html = False
        else:
            comment_str = '//'
            end_comment_str = ''
            is_html = False
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            while cursor.position() < end:
                cursor.movePosition(QTextCursor.StartOfLine)
                line = cursor.block().text().strip()
                if is_html:
                    if not line.startswith(comment_str):
                        cursor.insertText(comment_str + ' ')
                        cursor.movePosition(QTextCursor.EndOfLine)
                        cursor.insertText(' ' + end_comment_str)
                        end += len(comment_str) + len(end_comment_str) + 2
                else:
                    if not line.startswith(comment_str):
                        cursor.insertText(comment_str + ' ')
                        end += len(comment_str) + 1
                cursor.movePosition(QTextCursor.Down)
                if cursor.atEnd():
                    break
        else:
            cursor.movePosition(QTextCursor.StartOfLine)
            line = cursor.block().text().strip()
            if is_html:
                if not line.startswith(comment_str):
                    cursor.insertText(comment_str + ' ')
                    cursor.movePosition(QTextCursor.EndOfLine)
                    cursor.insertText(' ' + end_comment_str)
            else:
                if not line.startswith(comment_str):
                    cursor.insertText(comment_str + ' ')
        cursor.endEditBlock()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area.line_number_width(), cr.height()))
        # Minimapa à direita
        self.minimap.move(self.width() - self.minimap.width() - 2, 2)
        self.minimap.setFixedHeight(self.height() - 4)
        # Posiciona a barra de busca no topo do editor
        self.search_bar.setGeometry(10, 10, self.width() - 20, 36)

    def toggle_search_bar(self):
        self.search_bar.setVisible(not self.search_bar.isVisible())
        if self.search_bar.isVisible():
            self.search_input.setFocus()

    def incremental_search(self, forward=True):
        text = self.search_input.text()
        if not text:
            self.moveCursor(QTextCursor.Start)
            self.setExtraSelections([])
            return
        flags = QTextDocument.FindFlags()
        if not forward:
            flags |= QTextDocument.FindBackward
        found = self.find(text, flags)
        # Realce todas as ocorrências
        extra = []
        cursor = self.document().find(text)
        while not cursor.isNull():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor('#264f78'))
            sel.cursor = cursor
            extra.append(sel)
            cursor = self.document().find(text, cursor)
        self.setExtraSelections(extra)

    def replace_one(self):
        if self.textCursor().hasSelection():
            self.textCursor().insertText(self.replace_input.text())
            self.incremental_search()

    def replace_all(self):
        text = self.search_input.text()
        replace = self.replace_input.text()
        if not text:
            return
        content = self.toPlainText().replace(text, replace)
        self.setPlainText(content)
        self.incremental_search()
        # Auto-complete básico
        keywords = [
            # HTML
            'html', 'head', 'body', 'div', 'span', 'script', 'style', 'link', 'meta', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button', 'label', 'select', 'option', 'textarea',
            # CSS
            'color', 'background', 'margin', 'padding', 'border', 'display', 'flex', 'grid', 'font-size', 'font-family', 'width', 'height', 'position', 'absolute', 'relative', 'fixed', 'float', 'clear', 'overflow', 'z-index', 'align-items', 'justify-content',
            # JS
            'function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return', 'document', 'window', 'addEventListener', 'querySelector', 'getElementById', 'console', 'log', 'alert', 'setTimeout', 'setInterval', 'class', 'constructor', 'this', 'new', 'import', 'export'
        ]
        self.completer = QCompleter(keywords + self.get_document_words(), self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insert_completion)

    def get_document_words(self):
        text = self.toPlainText()
        words = set([w for w in text.split() if len(w) > 2])
        return list(words)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        # Atualiza palavras do documento no completer
        self.completer.model().setStringList(list(set(self.completer.model().stringList() + self.get_document_words())))
        if event.text() and event.text()[-1].isalnum():
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            prefix = cursor.selectedText()
            if prefix:
                self.completer.setCompletionPrefix(prefix)
                cr = self.cursorRect()
                cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                                    + self.completer.popup().verticalScrollBar().sizeHint().width())
                self.completer.complete(cr)

    def insert_completion(self, completion):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        tc.removeSelectedText()
        tc.insertText(completion)
        self.setTextCursor(tc)
        # Dobramento de código (code folding) simples
        self.folded_blocks = set()
        self.folding_btns = []
        self.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.viewport() and event.type() == event.MouseButtonPress:
            pos = event.pos()
            block = self.cursorForPosition(pos).block()
            text = block.text().strip()
            # Detecta início de bloco (ex: {, <div>, function)
            if text.endswith('{') or text.startswith('<div') or text.startswith('function'):
                block_num = block.blockNumber()
                if block_num in self.folded_blocks:
                    self.unfold_block(block_num)
                else:
                    self.fold_block(block_num)
                return True
        return super().eventFilter(obj, event)

    def fold_block(self, block_num):
        doc = self.document()
        block = doc.findBlockByNumber(block_num)
        start = block.position() + len(block.text())
        end = self.find_block_end(block)
        cursor = self.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        self.folded_blocks.add(block_num)

    def unfold_block(self, block_num):
        # Não destrutivo: recarrega o texto original (simples)
        # Para produção, salve o texto dobrado em cache
        # self.setPlainText(self.toPlainText())
        self.folded_blocks.remove(block_num)

    def find_block_end(self, block):
        # Busca fim do bloco para { ... } ou <div> ... </div>
        text = self.toPlainText()
        pos = block.position() + len(block.text())
        stack = 1
        i = pos
        while i < len(text):
            if text[i] == '{':
                stack += 1
            elif text[i] == '}':
                stack -= 1
                if stack == 0:
                    return i+1
            i += 1
        return len(text)

    def select_next_occurrence(self):
        """Seleciona a próxima ocorrência da palavra selecionada (Ctrl+D)."""
        cursor = self.textCursor()
        selected = cursor.selectedText()
        if not selected:
            # Se nada selecionado, seleciona a palavra sob o cursor
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            self.setTextCursor(cursor)
            selected = cursor.selectedText()
            if not selected:
                return
        # Procura próxima ocorrência após o cursor
        doc = self.document()
        start = cursor.selectionEnd()
        found = doc.find(selected, start)
        if found.isNull():
            # Se não achou, procura do início
            found = doc.find(selected, 0)
        if not found.isNull():
            # Adiciona seleção extra
            extra = self.extraSelections()
            sel = QTextEdit.ExtraSelection()
            sel.cursor = found
            sel.format.setBackground(QColor('#264f78'))
            extra.append(sel)
            self.setExtraSelections(extra)

    def toggle_theme(self):
        # Alterna entre tema claro e escuro
        if hasattr(self, 'theme') and hasattr(self, 'dark_qss') and hasattr(self, 'light_qss'):
            if self.theme == 'dark':
                self.theme = 'light'
                self.setStyleSheet(self.light_qss)
            else:
                self.theme = 'dark'
                self.setStyleSheet(self.dark_qss)

    def update_line_number_area_width(self, _=None):
        """Atualiza a largura da área de numeração de linhas."""
        if hasattr(self, 'line_number_area'):
            self.setViewportMargins(self.line_number_area.line_number_width(), 0, 0, 0)

    def update_line_number_area(self):
        """Atualiza a área de numeração de linhas."""
        rect = self.contentsRect()
        self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        self.update_line_number_area_width()

    def highlight_current_line(self):
        """Destaca a linha atual no editor."""
        extraSelections = []
        if not self.isReadOnly():
            from PyQt6.QtGui import QTextCursor, QTextFormat, QColor
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor('#23272e'))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def update_minimap(self):
        """Atualiza o conteúdo do minimapa com o texto atual do editor."""
        if hasattr(self, 'minimap'):
            self.minimap.setPlainText(self.toPlainText())

    def sync_minimap_scroll(self, value):
        """Sincroniza o scroll vertical do minimapa com o editor principal."""
        if hasattr(self, 'minimap'):
            self.minimap.verticalScrollBar().setValue(value)

    def run_linting(self):
        """Placeholder para linting de código. Não faz nada por enquanto."""
        pass

    def load_content(self):
        """Placeholder para carregar conteúdo. Não faz nada por enquanto."""
        pass
