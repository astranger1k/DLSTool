"""Qt XML syntax highlighter utilities."""
from PySide6 import QtCore, QtGui


class XMLHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for XML text documents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []

        tag_format = QtGui.QTextCharFormat()
        tag_format.setForeground(QtGui.QColor("#0080FF"))
        tag_format.setFontWeight(QtGui.QFont.Weight.Bold)
        self.highlightingRules.append((r'<[/?]?[A-Za-z_][\w:.-]*', tag_format))
        self.highlightingRules.append((r'[/?]?>', tag_format))

        attribute_format = QtGui.QTextCharFormat()
        attribute_format.setForeground(QtGui.QColor("#FF8000"))
        self.highlightingRules.append((r'\b[A-Za-z_][\w:.-]*(?==)', attribute_format))

        value_format = QtGui.QTextCharFormat()
        value_format.setForeground(QtGui.QColor("#00AA00"))
        self.highlightingRules.append((r'"[^"]*"', value_format))
        self.highlightingRules.append((r"'[^']*'", value_format))

        comment_format = QtGui.QTextCharFormat()
        comment_format.setForeground(QtGui.QColor("#808080"))
        comment_format.setFontItalic(True)
        self.highlightingRules.append((r'<!--.*?-->', comment_format))

        number_format = QtGui.QTextCharFormat()
        number_format.setForeground(QtGui.QColor("#FF00FF"))
        self.highlightingRules.append((r'\b\d+\.?\d*\b', number_format))

        self.rules = []
        for pattern, fmt in self.highlightingRules:
            self.rules.append((QtCore.QRegularExpression(pattern), fmt))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            expression = pattern
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
