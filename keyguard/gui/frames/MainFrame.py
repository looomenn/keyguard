"""Main Frame."""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy, QLabel, QVBoxLayout, QStackedWidget
)
from PyQt6.QtCore import Qt

from .CardFrame import CardFrame
from .TrainingFrame import TrainingFrame
from .AuthFrame import AuthFrame


class MainFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.train_card = CardFrame(
            "Тренування",
            parent=self,
            image_path="keyguard/resources/training.svg"
        )
        self.auth_card = CardFrame(
            "Авторизація",
            parent=self,
            image_path="keyguard/resources/locker.svg"
        )

        for card in (self.train_card, self.auth_card):
            card.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
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

        # self.train_card.clicked.connect(lambda: self.stack.setCurrentWidget(1))

        # cards_group = QHBoxLayout()
        # cards_group.setContentsMargins(0, 0, 0, 0)
        # cards_group.setSpacing(0)
        # cards_group.addWidget(self.train_card, stretch=1)
        # cards_group.addWidget(self.auth_card, stretch=1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        layout.addWidget(self.stack)

        self.setLayout(layout)

    def open_training(self):
        self.training_window = TrainingFrame()
        self.training_window.show()
