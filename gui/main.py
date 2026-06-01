"""
Entry point for the TestLink PFS Client GUI application.

Run with:
    python gui/main.py              (from the project root)
    python -m gui.main              (from the project root)

Requires PyQt5.  A dark theme is applied if qdarkstyle is installed;
otherwise the built-in Fusion style with a hand-tuned dark palette is used.
"""

import sys
from pathlib import Path

# ── Path setup ─────────────────────────────────────────────────────────────────
# Insert the project root so `gui.*` and `src.*` packages are importable.
_PROJECT_ROOT = Path(__file__).parent.parent
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── PyQt5 guard ────────────────────────────────────────────────────────────────
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPalette, QColor
except ImportError:
    print(
        "ERROR: PyQt5 is not installed.\n"
        "Install with:  pip install PyQt5\n"
        "Or with dark theme:  pip install PyQt5 qdarkstyle"
    )
    sys.exit(1)


# ── Dark palette (fallback when qdarkstyle is absent) ─────────────────────────

def _make_dark_palette() -> QPalette:
    """Return a dark QPalette compatible with the Fusion style."""
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(45, 45, 48))
    pal.setColor(QPalette.WindowText,      QColor(220, 220, 220))
    pal.setColor(QPalette.Base,            QColor(30, 30, 30))
    pal.setColor(QPalette.AlternateBase,   QColor(45, 45, 48))
    pal.setColor(QPalette.ToolTipBase,     QColor(30, 30, 30))
    pal.setColor(QPalette.ToolTipText,     QColor(220, 220, 220))
    pal.setColor(QPalette.Text,            QColor(220, 220, 220))
    pal.setColor(QPalette.Button,          QColor(55, 55, 60))
    pal.setColor(QPalette.ButtonText,      QColor(220, 220, 220))
    pal.setColor(QPalette.BrightText,      Qt.red)
    pal.setColor(QPalette.Link,            QColor(42, 130, 218))
    pal.setColor(QPalette.Highlight,       QColor(42, 130, 218))
    pal.setColor(QPalette.HighlightedText, QColor(20, 20, 20))
    # Disabled states
    pal.setColor(QPalette.Disabled, QPalette.Text,       QColor(120, 120, 120))
    pal.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 120, 120))
    pal.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 120, 120))
    return pal


# ── Application entry point ───────────────────────────────────────────────────

def main():
    """Create the QApplication, apply theming, and show the MainWindow."""
    app = QApplication(sys.argv)
    app.setApplicationName("TestLink PFS Client")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Benchmark Electronics")
    app.setOrganizationDomain("benchmark.com")

    # Apply dark theme (prefer qdarkstyle, fall back to Fusion + dark palette)
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))
    except ImportError:
        app.setStyle("Fusion")
        app.setPalette(_make_dark_palette())
        # Minimal stylesheet tweaks for Fusion dark
        app.setStyleSheet(
            "QToolTip { color: #ddd; background-color: #2d2d30; border: 1px solid #555; }"
            "QGroupBox { border: 1px solid #555; border-radius: 4px; margin-top: 8px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }"
        )

    # Import MainWindow after path setup
    from gui.main_window import MainWindow

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
