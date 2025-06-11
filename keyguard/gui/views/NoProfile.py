from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from keyguard.gui.components.components import Button


class NoProfile(QWidget):
    """Empty state widget.

    A widget shown when no profile exists or profile has no runs.

    Signals:
        start_training: The signal emitted when the button is pressed.
    """

    start_training = pyqtSignal()

    def __init__(
        self,
        mode: str = "training",
        parent: QWidget | None = None,
    ) -> None:
        """Initialize an instance of the NoProfile class.

        Args:
            mode: The mode of the widget.
            parent: The parent widget.

        Returns:
            None
        """
        super().__init__(parent)
        self.mode = mode  # "training" or "auth"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        center = QWidget()

        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sad_face = QLabel("(>_<)")
        sad_face.setProperty("class", "blank_state-emoji")
        sad_face.setAlignment(Qt.AlignmentFlag.AlignCenter)

        headline = QLabel(
            "Профіль не знайдено" if mode == "training" else "Недостатньо даних"
        )
        headline.setProperty("class", "blank_state-heading")
        headline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtext = QLabel(
            "Почніть тренування, щоб сформувати профіль"
            if mode == "training"
            else "Для автентифікації потрібно спочатку пройти тренування"
        )
        subtext.setProperty("class", "blank_state-description")
        subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = Button("Почати тренування", primary=True)
        btn.setProperty("class", "blank_state-action")
        btn.setFixedWidth(180)
        btn.clicked.connect(self.start_training.emit)

        center_layout.addWidget(sad_face)
        center_layout.addWidget(headline)
        center_layout.addWidget(subtext)
        center_layout.addSpacing(8)
        center_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(center, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
