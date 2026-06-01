"""
Connection test dialog.

Runs TestLinkClient connectivity in a QThread so the GUI stays responsive.
Shows an indeterminate progress bar while testing and displays a success or
failure message when the thread completes.
"""

import sys
from pathlib import Path

# Ensure src/ is importable
_SRC_DIR = str(Path(__file__).parent.parent.parent / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

try:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QProgressBar,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
except ImportError as exc:
    print(f"PyQt5 is required. Install with: pip install PyQt5\n{exc}")
    sys.exit(1)


# ── Background worker ─────────────────────────────────────────────────────────

class _ConnectionWorker(QObject):
    """
    Runs a lightweight PFS connectivity check in a background thread.

    Signals:
        success(str): Human-readable success message.
        failure(str): Human-readable error description.
    """

    success = pyqtSignal(str)
    failure = pyqtSignal(str)

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

    def run(self):
        """Attempt send_command('PfsGetSystemInfo') and emit success/failure."""
        try:
            from testlink_client import TestLinkClient
            client = TestLinkClient(
                host=self.config["host"],
                database=self.config["database"],
                port=int(self.config.get("port", 50000)),
                timeout=min(int(self.config.get("timeout", 30)), 15),
                work_center=self.config.get("work_center") or None,
                validate_cert=bool(self.config.get("validate_cert", True)),
            )
            status, message, _ = client.send_command(
                "PfsGetSystemInfo",
                {},
                user_id=self.config.get("user_id") or None,
                password=self.config.get("password") or None,
            )
            self.success.emit(f"{status.value}: {message}")
        except Exception as exc:
            self.failure.emit(f"{type(exc).__name__}: {exc}")


# ── Dialog ─────────────────────────────────────────────────────────────────────

class ConnectionDialog(QDialog):
    """
    Modal dialog that tests connectivity to the PFS server.

    A background QThread runs the connection check.  On completion the dialog
    either accepts (success) or stays open showing the error.

    Args:
        config: Dict from ConfigPanel.get_config().
        parent: Optional parent widget.

    Returns (via exec_()):
        QDialog.Accepted if the connection succeeded.
        QDialog.Rejected if the user closed without success.
    """

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self._thread: QThread = None
        self._worker: _ConnectionWorker = None
        self._setup_ui()
        self._start_test()

    # ── Setup ──────────────────────────────────────────────────────────

    def _setup_ui(self):
        self.setWindowTitle("Test Connection")
        self.setModal(True)
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        host = self.config.get("host", "")
        port = self.config.get("port", 50000)
        db   = self.config.get("database", "")

        self.info_label = QLabel(
            f"Testing connection to <b>{host}:{port}</b> / database <b>{db}</b>…"
        )
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        layout.addWidget(self.progress)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        self.btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.btn_box.rejected.connect(self.reject)
        self.btn_box.setEnabled(False)
        layout.addWidget(self.btn_box)

    # ── Thread management ──────────────────────────────────────────────

    def _start_test(self):
        """Spin up the background thread and start the worker."""
        self._worker = _ConnectionWorker(self.config)
        self._thread = QThread(self)

        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.success.connect(self._on_success)
        self._worker.failure.connect(self._on_failure)
        self._worker.success.connect(self._thread.quit)
        self._worker.failure.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    # ── Slot handlers ──────────────────────────────────────────────────

    def _on_success(self, message: str):
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.info_label.setText("Connection successful!")
        self.result_label.setText(f"✓  {message}")
        self.result_label.setStyleSheet("color: #6bcb77; font-weight: bold;")
        self.btn_box.setEnabled(True)
        # Auto-accept so MainWindow can update status bar
        self.accept()

    def _on_failure(self, message: str):
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.info_label.setText("Connection failed.")
        self.result_label.setText(f"✗  {message}")
        self.result_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        self.btn_box.setEnabled(True)
