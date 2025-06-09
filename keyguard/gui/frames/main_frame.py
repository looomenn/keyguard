"""Main Frame."""

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .auth_frame import AuthFrame
from .CardFrame import CardFrame
from .TrainingFrame import TrainingFrame


class MainFrame(QWidget):
    """MainFrame class."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize MainFrame.

        Args:
            parent: the parent widget
        """
        super().__init__(parent)

        self.train_card = CardFrame(
            "Тренування", parent=self, image_path="resources/training.svg"
        )
        self.auth_card = CardFrame(
            "Авторизація", parent=self, image_path="resources/locker.svg"
        )

        for card in (self.train_card, self.auth_card):
            card.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )

        home_page = QWidget(self)
        home_layout = QHBoxLayout(home_page)
        home_layout.setContentsMargins(0, 0, 0, 0)
        home_layout.setSpacing(0)
        home_layout.addWidget(self.train_card, stretch=1)
        home_layout.addWidget(self.auth_card, stretch=1)

        self.training_page = TrainingFrame(parent=self)
        self.auth_page = AuthFrame(parent=self)

        self.stack = QStackedWidget(self)
        self.stack.addWidget(home_page)
        self.stack.addWidget(self.training_page)
        self.stack.addWidget(self.auth_page)

        self.train_card.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.training_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.auth_card.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.auth_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.auth_page.switch_to_training.connect(lambda: self.stack.setCurrentIndex(1))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        layout.addWidget(self.stack)

        self.setLayout(layout)

    def open_training(self) -> None:
        """Open the training window."""
        self.training_window = TrainingFrame()
        self.training_window.show()
