from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from keyguard.gui.components.components import Button


class DashboardView(QWidget):
    """Widget shown when no profile exists or profile has no runs."""

    exit_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize DashboardView.

        Args:
            parent: the parent widget
        """
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        center = QWidget()

        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        emoji = QLabel("^_^")
        emoji.setProperty("class", "blank_state-emoji")
        emoji.setAlignment(Qt.AlignmentFlag.AlignCenter)

        headline = QLabel("O, я знаю тебе!")
        headline.setProperty("class", "blank_state-heading")
        headline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtext = QLabel("Ви успішно автентифіковані!")
        subtext.setProperty("class", "blank_state-description")
        subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = Button("Вийти", primary=True)
        btn.setProperty("class", "blank_state-action")
        btn.setFixedWidth(180)
        btn.clicked.connect(self.exit_clicked.emit)

        center_layout.addWidget(emoji)
        center_layout.addWidget(headline)
        center_layout.addWidget(subtext)
        center_layout.addSpacing(8)
        center_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(center, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
