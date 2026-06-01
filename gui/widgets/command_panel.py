"""
Procedure selector with dynamic parameter forms, live request preview, and Execute button.

Procedure categories and their parameter lists are discovered dynamically via the
PROCEDURE_NAME / REQUIRED_PARAMS / OPTIONAL_PARAMS class attributes defined in
src/procedures/.
"""

import sys
from pathlib import Path

# Ensure src/ is importable from this widget's location
_SRC_DIR = str(Path(__file__).parent.parent.parent / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
        QListWidget, QListWidgetItem, QFormLayout, QLineEdit,
        QPushButton, QTextEdit, QGroupBox, QScrollArea,
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont, QColor
except ImportError as exc:
    print(f"PyQt5 is required. Install with: pip install PyQt5\n{exc}")
    sys.exit(1)


# ── Category membership sets ──────────────────────────────────────────────────

TRANSACTION_PROCS = frozenset({
    "PfsVerifyUserInput", "PfsSendResults", "PfsSendSignoff", "PfsPanelize",
    "PfsLinkCompData", "PfsFindSerialNumber", "PfsGenerateSerialNumbers",
    "PfsSetHalt", "PfsClearHalt",
})

RETRIEVAL_PROCS = frozenset({
    "PfsGetDefectCodes", "PfsGetOperationCodes", "PfsGetWorkCenters",
    "PfsGetRepairCodes", "PfsGetBomItems", "PfsGetSerialNumbers",
    "PfsGetSnDefects", "PfsGetSnHistory", "PfsGetSnLinkedData",
    "PfsGetSnMacAddresses", "PfsGetSnPanelNumber", "PfsGetSnParentItemInfo",
    "PfsGetSnStatus", "PfsGetSnSwitchInfo", "PfsGetPnlSerialNumbers",
    "PfsGetProductionOrderInfo", "PfsGetItemInfo", "PfsGetUsageItems",
    "PfsGetCurrentUserInfo", "PfsGetFeederInfo", "PfsGetMachineShares",
    "PfsGetMacAddrSerialNumber", "PfsGetWorkInstructions",
    "PfsGetWorkInstructionOperations", "PfsGetWorkInstructionMachines",
})

UTILITY_PROCS = frozenset({
    "PfsQuery", "PfsExecuteProcedure", "PfsGenerateReport", "PfsExportData",
    "PfsImportData", "PfsGetSystemInfo", "PfsBackupDatabase", "PfsRestoreDatabase",
    "PfsGetAuditLog", "PfsGetUsers", "PfsGetUserRoles",
})

_CATEGORY_COLORS = {
    "Transaction": "#ff9f43",
    "Retrieval":   "#54a0ff",
    "Utility":     "#a29bfe",
}

# Params pre-populated from the config panel (shown in form but auto-filled)
_CONFIG_PARAM_MAP = {
    "DATABASE":    "database",
    "USER_ID":     "user_id",
    "PASSWORD":    "password",
    "WORK_CENTER": "work_center",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _norm_params(params) -> list:
    """Return a list of param name strings from a list or dict declaration."""
    if isinstance(params, dict):
        return list(params.keys())
    if isinstance(params, list):
        return list(params)
    return []


def _get_category(proc_name: str) -> str:
    if proc_name in TRANSACTION_PROCS:
        return "Transaction"
    if proc_name in RETRIEVAL_PROCS:
        return "Retrieval"
    if proc_name in UTILITY_PROCS:
        return "Utility"
    return "Unknown"


def _load_all_procedures() -> dict:
    """
    Import every procedure class exported by src/procedures/__init__.py.

    Returns:
        Mapping of procedure name string → procedure class.
        Non-class exports (template functions) are silently skipped.
    """
    result = {}
    try:
        import procedures as proc_mod
        for name in getattr(proc_mod, "__all__", []):
            cls = getattr(proc_mod, name, None)
            if cls is not None and hasattr(cls, "PROCEDURE_NAME") and hasattr(cls, "REQUIRED_PARAMS"):
                result[name] = cls
    except Exception as exc:
        print(f"Warning: could not load procedures: {exc}")
    return result


# ── ParamField ────────────────────────────────────────────────────────────────

class ParamField(QWidget):
    """Single labelled input row for one procedure parameter."""

    value_changed = pyqtSignal()

    def __init__(self, param_name: str, required: bool = False, parent=None):
        super().__init__(parent)
        self.param_name = param_name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("(required)" if required else "(optional)")
        if required:
            self.edit.setStyleSheet(
                "background-color: #3a2e00; border: 1px solid #aa8800;"
            )
        self.edit.textChanged.connect(self.value_changed.emit)
        layout.addWidget(self.edit)

    def get_value(self) -> str:
        return self.edit.text()

    def set_value(self, value: str):
        self.edit.setText(str(value) if value is not None else "")


# ── CommandPanel ──────────────────────────────────────────────────────────────

class CommandPanel(QWidget):
    """
    Procedure selector with dynamic parameter forms and an Execute button.

    Signals:
        execute_requested(procedure_class, params_dict):
            Emitted when the user clicks Execute.  *params_dict* contains
            only non-empty field values; DATABASE / USER_ID / PASSWORD are
            included so the caller can pass them on to send_command.

    Public methods:
        set_config(config_dict)  — pre-populate config-derived params.
        trigger_execute()        — programmatically fire Execute.
    """

    execute_requested = pyqtSignal(object, object)  # (class, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._procedures = _load_all_procedures()
        self._current_proc = None
        self._param_fields: dict = {}
        self._config: dict = {}
        self._setup_ui()
        self._populate_proc_list("All")

    # ── Setup ─────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Category filter row
        cat_row = QHBoxLayout()
        cat_row.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Transaction", "Retrieval", "Utility"])
        self.category_combo.currentTextChanged.connect(self._populate_proc_list)
        cat_row.addWidget(self.category_combo)
        layout.addLayout(cat_row)

        # Procedure list
        layout.addWidget(QLabel("Procedure:"))
        self.proc_list = QListWidget()
        self.proc_list.setMaximumHeight(160)
        self.proc_list.currentItemChanged.connect(self._on_proc_selected)
        layout.addWidget(self.proc_list)

        # Scrollable parameter form
        self.params_group = QGroupBox("Parameters")
        self._params_form = QFormLayout()
        self._params_form.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self._params_form.setLabelAlignment(Qt.AlignRight)
        self.params_group.setLayout(self._params_form)

        scroll = QScrollArea()
        scroll.setWidget(self.params_group)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(160)
        layout.addWidget(scroll, stretch=1)

        # Execute button
        self.execute_btn = QPushButton("▶   Execute")
        self.execute_btn.setMinimumHeight(42)
        self.execute_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #1a7a1a; color: white;"
            "  font-size: 14px; font-weight: bold; border-radius: 4px;"
            "}"
            "QPushButton:hover  { background-color: #228b22; }"
            "QPushButton:pressed { background-color: #145214; }"
            "QPushButton:disabled { background-color: #444; color: #777; }"
        )
        self.execute_btn.setEnabled(False)
        self.execute_btn.clicked.connect(self._on_execute_clicked)
        layout.addWidget(self.execute_btn)

        # Request preview
        preview_group = QGroupBox("Request Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(110)
        mono = QFont("Courier New", 9)
        mono.setStyleHint(QFont.Monospace)
        self.preview_text.setFont(mono)
        preview_layout.addWidget(self.preview_text)
        layout.addWidget(preview_group)

    # ── Procedure list ─────────────────────────────────────────────────

    def _populate_proc_list(self, category: str):
        """Rebuild the procedure list filtered by *category*."""
        self.proc_list.clear()
        filter_set = {
            "Transaction": TRANSACTION_PROCS,
            "Retrieval":   RETRIEVAL_PROCS,
            "Utility":     UTILITY_PROCS,
        }.get(category)  # None → show all

        for name in sorted(self._procedures):
            if filter_set is not None and name not in filter_set:
                continue
            item = QListWidgetItem(name)
            cat = _get_category(name)
            color = _CATEGORY_COLORS.get(cat, "#cccccc")
            item.setForeground(QColor(color))
            self.proc_list.addItem(item)

    # ── Procedure selection ─────────────────────────────────────────────

    def _on_proc_selected(self, current, _previous):
        """Rebuild parameter form when the user picks a different procedure."""
        if current is None:
            self._current_proc = None
            self.execute_btn.setEnabled(False)
            self.preview_text.clear()
            return

        self._current_proc = self._procedures.get(current.text())
        if self._current_proc:
            self._rebuild_param_form()
            self.execute_btn.setEnabled(True)

    # ── Parameter form ─────────────────────────────────────────────────

    def _rebuild_param_form(self):
        """Clear and regenerate the parameter form for the current procedure."""
        # Remove all existing rows
        while self._params_form.rowCount() > 0:
            self._params_form.removeRow(0)
        self._param_fields.clear()

        proc = self._current_proc
        required = _norm_params(proc.REQUIRED_PARAMS)
        optional = _norm_params(proc.OPTIONAL_PARAMS)

        # Required params — gold label, highlighted background
        for pname in required:
            field = ParamField(pname, required=True)
            self._prefill_field(field, pname)
            field.value_changed.connect(self._update_preview)

            label = QLabel(f"* {pname}:")
            label.setStyleSheet("color: #ffd93d; font-weight: bold;")
            self._params_form.addRow(label, field)
            self._param_fields[pname] = field

        # Optional params — standard label, faint background
        for pname in optional:
            if pname in self._param_fields:
                continue  # already added as required
            field = ParamField(pname, required=False)
            self._prefill_field(field, pname)
            field.value_changed.connect(self._update_preview)
            self._params_form.addRow(f"{pname}:", field)
            self._param_fields[pname] = field

        self._update_preview()

    def _prefill_field(self, field: ParamField, param_name: str):
        """Pre-populate a field from the stored config if the param maps to one."""
        config_key = _CONFIG_PARAM_MAP.get(param_name)
        if config_key and self._config.get(config_key):
            field.set_value(self._config[config_key])

    def _get_params_dict(self) -> dict:
        """Collect all non-empty field values as a plain dict."""
        return {
            name: field.get_value().strip()
            for name, field in self._param_fields.items()
            if field.get_value().strip()
        }

    def _update_preview(self):
        """Regenerate the request preview from current field values."""
        if not self._current_proc:
            self.preview_text.clear()
            return
        params = self._get_params_dict()
        lines = [f"REQUEST_TYPE={self._current_proc.PROCEDURE_NAME}"]
        lines += [f"{k}={v}" for k, v in params.items()]
        self.preview_text.setPlainText("\r\n".join(lines))

    # ── Public API ─────────────────────────────────────────────────────

    def set_config(self, config: dict):
        """
        Update config-derived pre-fills (called by MainWindow when config changes).

        Args:
            config: Dict from ConfigPanel.get_config().
        """
        self._config = config
        if self._current_proc:
            self._rebuild_param_form()

    def trigger_execute(self):
        """Programmatically click Execute (used by toolbar action)."""
        if self._current_proc and self.execute_btn.isEnabled():
            self._on_execute_clicked()

    # ── Execute ────────────────────────────────────────────────────────

    def _on_execute_clicked(self):
        """Emit execute_requested with the current procedure and params."""
        if not self._current_proc:
            return
        self.execute_requested.emit(self._current_proc, self._get_params_dict())
