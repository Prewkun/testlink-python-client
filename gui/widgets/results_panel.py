"""Results panel — displays procedure response status, raw text, and parsed data."""

import sys

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
        QTableWidget, QTableWidgetItem, QTabWidget, QPushButton, QHeaderView,
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
except ImportError as exc:
    print(f"PyQt5 is required. Install with: pip install PyQt5\n{exc}")
    sys.exit(1)


_STATUS_COLOR = {
    "OK":      "#6bcb77",
    "Warning": "#ffd93d",
    "Failure": "#ff6b6b",
    "Error":   "#ff6b6b",
    "Unknown": "#aaaaaa",
}


class ResultsPanel(QWidget):
    """
    Displays the outcome of a PFS procedure call.

    Tabs:
        - Raw Response: status, message, and raw data lines in monospace text.
        - Parsed Data:  semicolon-delimited data rendered as a QTableWidget.

    Public methods:
        display_result(status_name, message, data_lines, elapsed_ms)
        display_error(error_type, message)
        show_pending()
        clear_results()
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_ui(self):
        """Build the results panel layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Status + elapsed-time row
        status_row = QHBoxLayout()
        self.status_label = QLabel("No results yet")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        status_row.addWidget(self.status_label, stretch=1)
        status_row.addWidget(self.time_label)
        layout.addLayout(status_row)

        # Tab widget: Raw / Parsed
        tabs = QTabWidget()

        # Raw response tab
        self.raw_text = QTextEdit()
        self.raw_text.setReadOnly(True)
        mono = QFont("Courier New", 9)
        mono.setStyleHint(QFont.Monospace)
        self.raw_text.setFont(mono)
        tabs.addTab(self.raw_text, "Raw Response")

        # Parsed data tab
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.verticalHeader().setDefaultSectionSize(22)
        tabs.addTab(self.data_table, "Parsed Data")

        layout.addWidget(tabs, stretch=1)

        # Clear button
        clear_btn = QPushButton("Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def display_result(self, status_name: str, message: str, data_lines: list, elapsed_ms: float):
        """
        Render a successful (or warned/failed) command response.

        Args:
            status_name: One of OK, Warning, Failure, Error, Unknown.
            message:     First-line status message from the server.
            data_lines:  List of subsequent data lines (may be empty).
            elapsed_ms:  Round-trip time in milliseconds.
        """
        color = _STATUS_COLOR.get(status_name, "#aaaaaa")
        self.status_label.setText(f"● {status_name}  —  {message}")
        self.status_label.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 13px; padding: 4px;"
        )
        self.time_label.setText(f"{elapsed_ms:.0f} ms")

        # Build raw text
        lines = [f"Status:  {status_name}", f"Message: {message}", ""]
        if data_lines:
            lines.append("─── Data Lines ─────────────────────────────")
            lines.extend(data_lines)
        self.raw_text.setPlainText("\n".join(lines))

        self._populate_table(data_lines)

    def display_error(self, error_type: str, message: str):
        """
        Render an exception raised during command execution.

        Args:
            error_type: Exception class name (e.g. ConnectionException).
            message:    Exception message text.
        """
        self.status_label.setText(f"● {error_type}")
        self.status_label.setStyleSheet(
            "color: #ff6b6b; font-weight: bold; font-size: 13px; padding: 4px;"
        )
        self.time_label.setText("")
        self.raw_text.setPlainText(f"{error_type}:\n{message}")
        self.data_table.clearContents()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

    def show_pending(self):
        """Show an indeterminate 'running…' state while a command executes."""
        self.status_label.setText("⏳  Running…")
        self.status_label.setStyleSheet(
            "color: #ffd93d; font-weight: bold; font-size: 13px; padding: 4px;"
        )
        self.time_label.setText("")
        self.raw_text.clear()
        self.data_table.clearContents()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

    def clear_results(self):
        """Reset the panel to its initial empty state."""
        self.status_label.setText("No results yet")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        self.time_label.setText("")
        self.raw_text.clear()
        self.data_table.clearContents()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _populate_table(self, data_lines: list):
        """Parse semicolon-delimited data lines into the QTableWidget."""
        self.data_table.clearContents()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

        if not data_lines:
            return

        rows = [line.split(";") for line in data_lines if line.strip()]
        if not rows:
            return

        num_cols = max(len(r) for r in rows)
        self.data_table.setRowCount(len(rows))
        self.data_table.setColumnCount(num_cols)
        self.data_table.setHorizontalHeaderLabels(
            [f"Col {i + 1}" for i in range(num_cols)]
        )

        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                item = QTableWidgetItem(cell.strip())
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.data_table.setItem(row_idx, col_idx, item)
