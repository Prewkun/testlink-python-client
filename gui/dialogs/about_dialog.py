"""About dialog for TestLink PFS Client."""

import sys

try:
    from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
except ImportError as exc:
    print(f"PyQt5 is required. Install with: pip install PyQt5\n{exc}")
    sys.exit(1)


class AboutDialog(QDialog):
    """Displays application information, version, and author details."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Build the about dialog layout."""
        self.setWindowTitle("About TestLink PFS Client")
        self.setModal(True)
        self.setMinimumWidth(380)
        self.setMaximumWidth(480)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # App title
        title_lbl = QLabel("TestLink PFS Client")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        # Version
        version_lbl = QLabel("Version 1.0.0")
        version_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_lbl)

        # Separator line
        sep = QLabel()
        sep.setFrameShape(QLabel.HLine if hasattr(QLabel, "HLine") else 0)
        sep.setStyleSheet("border-top: 1px solid #666; margin: 4px 0;")
        layout.addWidget(sep)

        # Description
        desc_lbl = QLabel(
            "A PyQt5 GUI client for the PFS (Production Flow System) /\n"
            "TestLink API.\n\n"
            "Supports all 47 PFS procedures including Transaction,\n"
            "Retrieval, and Utility operations.\n\n"
            "Features:\n"
            "  • Dynamic procedure parameter forms\n"
            "  • Non-blocking threaded execution\n"
            "  • Color-coded results and log viewer\n"
            "  • TLS 1.2 encrypted communication\n"
            "  • Persistent configuration via QSettings"
        )
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(desc_lbl)

        # Author
        author_lbl = QLabel("© Benchmark Electronics, Inc.")
        author_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_lbl)

        # OK button
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
