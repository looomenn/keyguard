"""
KeyGuard - Entry point.

This script allows you to run KeyGuard as a standalone application from the
command line.

Usage:
------
To run this script, use the following command:

    python -m keyguard

Options:
--------
No options supported
"""
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel

from keyguard.gui.frames import MainFrame

from keyguard.config import APP_SIZE, APP_TITLE


class App(QMainWindow):
    """Represent the main application interface."""

    def __init__(self):
        """Initialize an instance of the App class."""
        # windows setup
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setFixedSize(APP_SIZE[0], APP_SIZE[1])
        self.center()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(32, 32, 32, 32)
        self.main_layout.setSpacing(0)

        label = QLabel("Made by ange1o — experienced procrastinator", self)
        label.setProperty("class", "card-title")
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setStyleSheet("QLabel { color:#808080}")

        self.setStyleSheet("background-color: #000000;")

        self.main_frame = MainFrame()
        self.main_layout.setSpacing(24)
        self.main_layout.addWidget(self.main_frame)
        self.main_layout.addWidget(label)

        self.init_shortcuts()

    def center(self) -> None:
        """Center the window on the screen."""
        frame_geometry = self.frameGeometry()
        screen_geometry = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_geometry)
        self.move(frame_geometry.topLeft())

    def init_shortcuts(self):
        """Initialize key bindings."""
        escape_shortcut = QShortcut(QKeySequence('Escape'), self)
        escape_shortcut.activated.connect(self.close)


if __name__ == "__main__":
    app = QApplication([])
    windows = App()
    windows.show()
    sys.exit(app.exec())
