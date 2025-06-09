"""Training Frame."""

import time

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from keyguard.config import PHRASE
from keyguard.gui.components.components import Button
from keyguard.gui.views.LearningView import LearningView
from keyguard.gui.views.NoProfile import NoProfile
from keyguard.gui.views.SessionStatsView import SessionStatsView
from keyguard.logic import update_aggregate_profile
from keyguard.utils import (
    create_profile,
    get_svg,
    load_profile,
    save_profile,
)


class TrainingFrame(QWidget):
    """Frame for training view."""

    back_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize TrainingFrame.

        Args:
            parent: the parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Keyguard — Тренування")

        header_frame = QFrame()
        header_frame.setProperty("class", "header-frame")

        header_left = QWidget()
        header_left_layout = QHBoxLayout(header_left)
        header_left_layout.setContentsMargins(0, 0, 0, 0)
        header_left_layout.setSpacing(16)

        header_right = QWidget()
        header_right_layout = QHBoxLayout(header_right)
        header_right_layout.setContentsMargins(0, 0, 0, 0)
        header_right_layout.setSpacing(16)

        back_btn = Button("< Назад")
        back_btn.clicked.connect(self.back_clicked.emit)

        logo = get_svg("resources/training.svg", self, width=32, height=32)

        header_title = QLabel("Тренування")
        header_title.setProperty("class", "header-title")

        header_left_layout.addWidget(back_btn)
        header_left_layout.addWidget(logo)
        header_left_layout.addWidget(header_title)
        header_left_layout.addStretch(1)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(0)
        header_layout.addWidget(header_left)
        header_layout.addWidget(header_right)

        content_frame = QFrame(self)
        content_frame.setObjectName("content-frame")
        content_frame.setStyleSheet(
            "#content-frame { border: 1px solid #333333; background: #000; }"
        )
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.content_stack = QStackedWidget()

        # stack 0: No Profile
        self.no_profile_widget = NoProfile()
        self.no_profile_widget.start_training.connect(self._start_training)
        self.content_stack.addWidget(self.no_profile_widget)

        # stack 1: Learning View
        self.learning_view = None

        # stack 2: Stats View
        self.stats_view = None

        content_layout.addWidget(self.content_stack, stretch=1)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(content_frame, stretch=1)

        self._update_state()

    def _update_state(self) -> None:
        """Update the state of the training frame."""
        profile = load_profile("profile.json")
        if not profile:
            self.content_stack.setCurrentWidget(self.no_profile_widget)
            return

        phrase = profile["phrase"]

        if self.learning_view:
            self.content_stack.removeWidget(self.learning_view)
            self.learning_view.deleteLater()

        if self.stats_view:
            self.content_stack.removeWidget(self.stats_view)
            self.stats_view.deleteLater()
            self.stats_view = None

        self.learning_view = LearningView(phrase, profile)
        self.learning_view.session_complete.connect(self._on_session_complete)
        self.learning_view.session_cancelled.connect(self._update_state)
        self.learning_view.show_stats.connect(self._show_stats)
        self.learning_view.state_changed.connect(self._on_state_changed)
        self.content_stack.addWidget(self.learning_view)
        self.content_stack.setCurrentWidget(self.learning_view)

    def _start_training(self) -> None:
        """Start training by creating a new profile."""
        profile = create_profile(PHRASE)
        save_profile(profile, "profile.json")
        self._update_state()

    def _show_stats(self, session: dict) -> None:
        """Show the stats view with session data.

        Args:
            session: the session data
        """
        if not self.stats_view:
            self.stats_view = SessionStatsView(session)
            self.stats_view.back_clicked.connect(self._update_state)
            self.content_stack.addWidget(self.stats_view)

        self.stats_view.session = session
        self.stats_view.update_display()

        self.content_stack.setCurrentWidget(self.stats_view)

    def _on_session_complete(self, session: dict) -> None:
        """Handle session completion.

        Args:
            session: the session data
        """
        profile = load_profile("profile.json")

        session["timestamp"] = int(time.time())

        if "sessions" not in profile:
            profile["sessions"] = []
        profile["sessions"].append(session)

        update_aggregate_profile(profile, session)
        profile["updated"] = time.strftime(
            "%Y-%m-%d %H:%M", time.localtime(int(time.time()))
        )

        save_profile(profile, "profile.json")
        self._update_state()

    def _on_state_changed(self, state: int) -> None:
        """Handle state changes from LearningView.

        Args:
            state: the state of the training frame
        """
        if state == 0:
            self._update_state()
