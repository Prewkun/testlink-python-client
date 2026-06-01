"""Server/database/credentials configuration panel."""

import sys
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QGroupBox, QFormLayout, QLineEdit, QSpinBox,
        QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout,
    )
    from PyQt5.QtCore import pyqtSignal, QSettings, Qt
except ImportError as exc:
    print(f"PyQt5 is required. Install with: pip install PyQt5\n{exc}")
    sys.exit(1)


class ConfigPanel(QGroupBox):
    """
    Collapsible form for PFS server connection settings.

    Signals:
        config_changed(dict): Emitted whenever any field value changes.

    Public methods:
        get_config() -> dict
        set_config(dict)
        save_settings(QSettings)
        load_settings(QSettings)
    """

    config_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__("Server Configuration", parent)
        self._setup_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_ui(self):
        """Build the configuration form."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignLeft)

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("e.g. pfs-server.example.com")

        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(50000)

        self.database_edit = QLineEdit()
        self.database_edit.setPlaceholderText("e.g. PFSHJP4")

        self.user_edit = QLineEdit()
        self.user_edit.setPlaceholderText("Operator login ID")

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Operator password")

        self.workcenter_edit = QLineEdit()
        self.workcenter_edit.setPlaceholderText("Optional default work center")

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" sec")

        self.validate_cert_cb = QCheckBox("Validate TLS Certificate")
        self.validate_cert_cb.setChecked(True)

        form.addRow("Host:", self.host_edit)
        form.addRow("Port:", self.port_spin)
        form.addRow("Database:", self.database_edit)
        form.addRow("User ID:", self.user_edit)
        form.addRow("Password:", self.password_edit)
        form.addRow("Work Center:", self.workcenter_edit)
        form.addRow("Timeout:", self.timeout_spin)
        form.addRow("", self.validate_cert_cb)
        outer.addLayout(form)

        # Save / Load buttons
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save Config")
        self.save_btn.setToolTip("Persist configuration to QSettings")
        self.load_btn = QPushButton("Load Config")
        self.load_btn.setToolTip("Restore configuration from QSettings")
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.load_btn)
        outer.addLayout(btn_row)

    def _connect_signals(self):
        """Wire internal change signals to _emit_config_changed."""
        for widget in (self.host_edit, self.database_edit, self.user_edit,
                       self.password_edit, self.workcenter_edit):
            widget.textChanged.connect(self._emit_config_changed)
        self.port_spin.valueChanged.connect(self._emit_config_changed)
        self.timeout_spin.valueChanged.connect(self._emit_config_changed)
        self.validate_cert_cb.toggled.connect(self._emit_config_changed)
        self.save_btn.clicked.connect(self._save_to_settings)
        self.load_btn.clicked.connect(self._load_from_settings)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_config(self) -> dict:
        """Return current form values as a plain dictionary."""
        return {
            "host":          self.host_edit.text().strip(),
            "port":          self.port_spin.value(),
            "database":      self.database_edit.text().strip(),
            "user_id":       self.user_edit.text().strip(),
            "password":      self.password_edit.text(),
            "work_center":   self.workcenter_edit.text().strip(),
            "timeout":       self.timeout_spin.value(),
            "validate_cert": self.validate_cert_cb.isChecked(),
        }

    def set_config(self, config: dict):
        """Populate form fields from *config* dict (missing keys are ignored)."""
        self.host_edit.setText(config.get("host", ""))
        self.port_spin.setValue(int(config.get("port", 50000)))
        self.database_edit.setText(config.get("database", ""))
        self.user_edit.setText(config.get("user_id", ""))
        self.password_edit.setText(config.get("password", ""))
        self.workcenter_edit.setText(config.get("work_center", ""))
        self.timeout_spin.setValue(int(config.get("timeout", 30)))
        self.validate_cert_cb.setChecked(bool(config.get("validate_cert", True)))

    def save_settings(self, settings: QSettings):
        """Write current config to *settings* (password is intentionally skipped)."""
        cfg = self.get_config()
        for key, value in cfg.items():
            if key != "password":
                settings.setValue(f"config/{key}", value)

    def load_settings(self, settings: QSettings):
        """Read config from *settings* and update form fields."""
        cfg = {
            "host":          settings.value("config/host", ""),
            "port":          int(settings.value("config/port", 50000)),
            "database":      settings.value("config/database", ""),
            "user_id":       settings.value("config/user_id", ""),
            "work_center":   settings.value("config/work_center", ""),
            "timeout":       int(settings.value("config/timeout", 30)),
            "validate_cert": settings.value("config/validate_cert", True, type=bool),
        }
        self.set_config(cfg)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _emit_config_changed(self, *_args):
        """Emit config_changed with the current config dict."""
        self.config_changed.emit(self.get_config())

    def _save_to_settings(self):
        settings = QSettings("BenchmarkElectronics", "TestLinkPFSClient")
        self.save_settings(settings)

    def _load_from_settings(self):
        settings = QSettings("BenchmarkElectronics", "TestLinkPFSClient")
        self.load_settings(settings)
