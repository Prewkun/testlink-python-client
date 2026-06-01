"""
Main window for TestLink PFS Client.

Layout
------
┌─────────────────────────────────────────────────────────┐
│  Menu bar  │  Toolbar                                    │
├─────────────────────────────────────────────────────────┤
│ ConfigPanel │ QTabWidget                                 │
│ ─────────── │   • Results (ResultsPanel)                 │
│ CommandPanel│   • Log    (LogViewer)                     │
├─────────────────────────────────────────────────────────┤
│  Status bar                                             │
└─────────────────────────────────────────────────────────┘

The Execute flow runs entirely in a background QThread so the GUI never blocks.
"""

import sys
import time
from pathlib import Path

# Ensure src/ is importable before any local imports
_PROJECT_ROOT = Path(__file__).parent.parent
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QSplitter, QTabWidget,
        QVBoxLayout, QAction, QLabel, QMessageBox,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QObject
except ImportError as exc:
    print(f"PyQt5 is required. Install with: pip install PyQt5\n{exc}")
    sys.exit(1)

from gui.widgets.config_panel import ConfigPanel
from gui.widgets.command_panel import CommandPanel
from gui.widgets.results_panel import ResultsPanel
from gui.widgets.log_viewer import LogViewer
from gui.dialogs.connection_dialog import ConnectionDialog
from gui.dialogs.about_dialog import AboutDialog


# ── Background execute worker ─────────────────────────────────────────────────

class _ExecuteWorker(QObject):
    """
    Runs a PFS send_command call in a background thread.

    Signals:
        result_ready(status_name, message, data_lines, elapsed_ms)
        error_occurred(error_type, error_message)
    """

    result_ready   = pyqtSignal(str, str, object, float)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, config: dict, procedure_class, params: dict):
        super().__init__()
        self.config = config
        self.procedure_class = procedure_class
        self.params = dict(params)

    def run(self):
        """Create a TestLinkClient and call send_command; emit the outcome."""
        from testlink_client import TestLinkClient

        start = time.monotonic()
        try:
            client = TestLinkClient(
                host=self.config["host"],
                database=self.config["database"],
                port=int(self.config.get("port", 50000)),
                timeout=int(self.config.get("timeout", 30)),
                work_center=self.config.get("work_center") or None,
                validate_cert=bool(self.config.get("validate_cert", True)),
            )

            # Resolve credentials: form fields take precedence over config
            user_id  = self.params.get("USER_ID")  or self.config.get("user_id")  or None
            password = self.params.get("PASSWORD") or self.config.get("password") or None

            status, message, data_lines = client.send_command(
                self.procedure_class.PROCEDURE_NAME,
                self.params,
                user_id=user_id,
                password=password,
            )
            elapsed = (time.monotonic() - start) * 1000.0
            self.result_ready.emit(status.value, message, data_lines, elapsed)

        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000.0
            self.error_occurred.emit(type(exc).__name__, str(exc))


# ── MainWindow ─────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    QMainWindow subclass — top-level application shell.

    Responsibilities:
    * Hosts ConfigPanel, CommandPanel, ResultsPanel, LogViewer.
    * Manages the Execute worker thread lifecycle.
    * Persists window geometry and config via QSettings.
    """

    def __init__(self):
        super().__init__()
        self._settings  = QSettings("BenchmarkElectronics", "TestLinkPFSClient")
        self._thread: QThread         = None
        self._worker: _ExecuteWorker  = None

        self._build_ui()
        self._build_menus()
        self._build_toolbar()
        self._connect_signals()
        self._restore_settings()

        self.log_viewer.append_log("INFO", "TestLink PFS Client started.")

    # ── UI construction ────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("TestLink PFS Client")
        self.setMinimumSize(1100, 720)

        # ── Central splitter ──────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Left side: ConfigPanel (top) + CommandPanel (bottom)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)

        self.config_panel  = ConfigPanel()
        self.command_panel = CommandPanel()
        left_layout.addWidget(self.config_panel)
        left_layout.addWidget(self.command_panel, stretch=1)

        # Right side: tabbed Results + Log
        self.tab_widget   = QTabWidget()
        self.results_panel = ResultsPanel()
        self.log_viewer    = LogViewer()
        self.tab_widget.addTab(self.results_panel, "Results")
        self.tab_widget.addTab(self.log_viewer,    "Log")

        splitter.addWidget(left)
        splitter.addWidget(self.tab_widget)
        splitter.setSizes([420, 680])

        # ── Status bar ────────────────────────────────────────────────
        self.conn_status_label = QLabel("  ● Not Connected  ")
        self.conn_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        self.statusBar().addWidget(self.conn_status_label)

    def _build_menus(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("File")
        exit_act = QAction("Exit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Tools
        tools_menu = mb.addMenu("Tools")
        test_conn_act = QAction("Test Connection", self)
        test_conn_act.triggered.connect(self._test_connection)
        tools_menu.addAction(test_conn_act)

        clear_log_act = QAction("Clear Log", self)
        clear_log_act.triggered.connect(self.log_viewer.clear_log)
        tools_menu.addAction(clear_log_act)

        # Help
        help_menu = mb.addMenu("Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    def _build_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)

        exec_act = QAction("▶  Execute", self)
        exec_act.setToolTip("Execute the selected procedure (Enter)")
        exec_act.setShortcut("Return")
        exec_act.triggered.connect(self.command_panel.trigger_execute)
        tb.addAction(exec_act)

        clear_act = QAction("🗑  Clear Results", self)
        clear_act.setToolTip("Clear the results panel")
        clear_act.triggered.connect(self.results_panel.clear_results)
        tb.addAction(clear_act)

        tb.addSeparator()

        conn_act = QAction("🔌  Test Connection", self)
        conn_act.setToolTip("Test connectivity to the configured PFS server")
        conn_act.triggered.connect(self._test_connection)
        tb.addAction(conn_act)

    def _connect_signals(self):
        self.config_panel.config_changed.connect(self._on_config_changed)
        self.command_panel.execute_requested.connect(self._on_execute_requested)

    # ── Settings persistence ──────────────────────────────────────────

    def _restore_settings(self):
        geom = self._settings.value("window/geometry")
        if geom:
            self.restoreGeometry(geom)
        self.config_panel.load_settings(self._settings)

    def closeEvent(self, event):
        self._settings.setValue("window/geometry", self.saveGeometry())
        self.config_panel.save_settings(self._settings)
        event.accept()

    # ── Signal handlers ───────────────────────────────────────────────

    def _on_config_changed(self, config: dict):
        """Reflect updated config in the status bar and command panel."""
        self.command_panel.set_config(config)
        host = config.get("host", "")
        db   = config.get("database", "")
        if host and db:
            port = config.get("port", 50000)
            self.conn_status_label.setText(f"  ● Config: {host}:{port} / {db}  ")
            self.conn_status_label.setStyleSheet("color: #ffd93d; font-weight: bold;")
        else:
            self.conn_status_label.setText("  ● Not Connected  ")
            self.conn_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    def _on_execute_requested(self, procedure_class, params: dict):
        """Validate config, then spawn Execute worker thread."""
        if self._thread and self._thread.isRunning():
            QMessageBox.warning(self, "Busy", "A command is already running. Please wait.")
            return

        config = self.config_panel.get_config()
        if not config.get("host") or not config.get("database"):
            QMessageBox.warning(
                self, "Configuration Required",
                "Please enter Host and Database before executing."
            )
            return

        proc_name = procedure_class.PROCEDURE_NAME
        self.log_viewer.append_log("INFO", f"Executing {proc_name} …")
        self.results_panel.show_pending()
        self.tab_widget.setCurrentIndex(0)  # switch to Results tab

        self._worker = _ExecuteWorker(config, procedure_class, params)
        self._thread = QThread(self)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.result_ready.connect(self._on_result_ready)
        self._worker.error_occurred.connect(self._on_error_occurred)
        self._worker.result_ready.connect(self._thread.quit)
        self._worker.error_occurred.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._clear_execute_worker_state)

        self._thread.start()

    def _clear_execute_worker_state(self):
        """Drop references to the finished thread and worker."""
        self._thread = None
        self._worker = None

    def _on_result_ready(self, status_name: str, message: str, data_lines, elapsed_ms: float):
        """Relay successful result to ResultsPanel and LogViewer."""
        self.results_panel.display_result(status_name, message, list(data_lines), elapsed_ms)

        level = "WARNING" if status_name == "Warning" else "INFO"
        self.log_viewer.append_log(
            level,
            f"Result: {status_name} — {message}  ({elapsed_ms:.0f} ms,"
            f" {len(data_lines)} data line(s))"
        )

        color = "#6bcb77" if status_name == "OK" else "#ffd93d"
        self.conn_status_label.setText(f"  ● Last: {status_name}  ")
        self.conn_status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _on_error_occurred(self, error_type: str, message: str):
        """Relay exception to ResultsPanel and LogViewer."""
        self.results_panel.display_error(error_type, message)
        self.log_viewer.append_log("ERROR", f"{error_type}: {message}")
        self.conn_status_label.setText(f"  ● Error: {error_type}  ")
        self.conn_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")

    # ── Dialogs ───────────────────────────────────────────────────────

    def _test_connection(self):
        config = self.config_panel.get_config()
        if not config.get("host") or not config.get("database"):
            QMessageBox.warning(
                self, "Configuration Required",
                "Please enter Host and Database before testing the connection."
            )
            return

        self.log_viewer.append_log("INFO", "Testing connection …")
        dialog = ConnectionDialog(config, self)
        result = dialog.exec_()

        if result == ConnectionDialog.Accepted:
            host = config["host"]
            db   = config["database"]
            self.conn_status_label.setText(f"  ● Connected: {host}/{db}  ")
            self.conn_status_label.setStyleSheet("color: #6bcb77; font-weight: bold;")
            self.log_viewer.append_log("SUCCESS", f"Connection to {host}/{db} successful.")
        else:
            self.log_viewer.append_log("WARNING", "Connection test failed or was cancelled.")

    def _show_about(self):
        AboutDialog(self).exec_()
