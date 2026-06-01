"""Color-coded, auto-scrolling log viewer widget."""

import sys
from datetime import datetime

try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
except ImportError as exc:
    print(f"PyQt5 is required. Install with: pip install PyQt5\n{exc}")
    sys.exit(1)


# Map log level to display color
_LEVEL_COLORS = {
    "INFO":    "#ffffff",
    "WARNING": "#ffd93d",
    "ERROR":   "#ff6b6b",
    "DEBUG":   "#aaaaaa",
    "SUCCESS": "#6bcb77",
}


class LogViewer(QWidget):
    """
    Read-only log message viewer with color-coded levels and auto-scroll.

    Usage::

        log = LogViewer()
        log.append_log("INFO", "Application started")
        log.append_log("ERROR", "Connection refused")
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_ui(self):
        """Build the log viewer layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        mono = QFont("Courier New", 9)
        mono.setStyleHint(QFont.Monospace)
        self.log_text.setFont(mono)
        layout.addWidget(self.log_text, stretch=1)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear Log")
        clear_btn.setToolTip("Clear all log entries")
        clear_btn.clicked.connect(self.clear_log)

        copy_btn = QPushButton("Copy All")
        copy_btn.setToolTip("Copy all log text to clipboard")
        copy_btn.clicked.connect(self._copy_all)

        btn_row.addStretch()
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(copy_btn)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def append_log(self, level: str, message: str):
        """
        Append a color-coded log entry and auto-scroll to bottom.

        Args:
            level:   Log level string — INFO, WARNING, ERROR, DEBUG, SUCCESS.
            message: Human-readable log message.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = _LEVEL_COLORS.get(level.upper(), "#ffffff")

        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)

        padded_level = f"{level.upper():7s}"
        cursor.insertText(f"[{timestamp}] [{padded_level}] {message}\n")

        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def clear_log(self):
        """Remove all log entries."""
        self.log_text.clear()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _copy_all(self):
        """Copy full log contents to the system clipboard."""
        QApplication.clipboard().setText(self.log_text.toPlainText())
