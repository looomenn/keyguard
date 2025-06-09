"""Training Frame."""

import time
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QVBoxLayout,
    QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from keyguard.utils import get_svg, load_profile, save_profile, create_profile, generate_session_id
from keyguard.gui.components.components import Button
from keyguard.gui.views.NoProfile import NoProfile
from keyguard.gui.views.LearningView import LearningView
from keyguard.logic import update_aggregate_profile
from keyguard.config import PHRASE

class TrainingFrame(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyguard — Тренування")

        # Header
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

        logo = get_svg("keyguard/resources/training.svg", self, width=32, height=32)

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

        # Content frame with border
        content_frame = QFrame(self)
        content_frame.setObjectName("content-frame")
        content_frame.setStyleSheet("#content-frame { border: 1px solid #333333; background: #000; }")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Stack for different views
        self.content_stack = QStackedWidget()
        
        # Stack 0: No Profile
        no_profile_widget = NoProfile()
        no_profile_widget.start_training.connect(self._start_training)
        self.content_stack.addWidget(no_profile_widget)
        
        # Stack 1: Learning View
        self.learning_view = None
        
        content_layout.addWidget(self.content_stack, stretch=1)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(content_frame, stretch=1)
        
        self._update_state()

    def _update_state(self):
        profile = load_profile("resources/profile.json")
        phrase = profile["phrase"] if profile else PHRASE
        
        if self.learning_view:
            self.content_stack.removeWidget(self.learning_view)
            self.learning_view.deleteLater()
            
        self.learning_view = LearningView(phrase, profile)
        self.learning_view.session_complete.connect(self._on_session_complete)
        self.learning_view.session_cancelled.connect(self._update_state)
        self.content_stack.addWidget(self.learning_view)
        self.content_stack.setCurrentWidget(self.learning_view)

    def _start_training(self):
        self._update_state()

    def _on_session_complete(self, session):
        profile = load_profile("resources/profile.json")
        if not profile:
            profile = create_profile(session.get("phrase", self.learning_view.phrase))
            
        session["timestamp"] = int(time.time())
        
        if "sessions" not in profile:
            profile["sessions"] = []
        profile["sessions"].append(session)
        
        update_aggregate_profile(profile, session)
        profile["updated"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(time.time())))
        
        save_profile(profile, "resources/profile.json")
        self._update_state()

    def _on_delete_profile(self):
        # TODO: implement profile deletion logic
        pass
