"""AuthFrame module."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from keyguard.gui.components.components import Button
from keyguard.gui.views.AuthView import AuthView
from keyguard.gui.views.DashboardView import DashboardView
from keyguard.gui.views.NoProfile import NoProfile
from keyguard.utils import get_svg, load_profile


class AuthFrame(QWidget):
    """Frame for authentication view."""

    back_clicked = pyqtSignal()
    switch_to_training = pyqtSignal()
    auth_success = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize AuthFrame.

        Args:
            parent: the parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Keyguard — Авторизація")

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

        logo = get_svg("resources/locker.svg", self, width=32, height=32)

        header_title = QLabel("Авторизація")
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
        self.no_profile_widget = NoProfile(mode="auth")
        self.no_profile_widget.start_training.connect(self.switch_to_training.emit)
        self.content_stack.addWidget(self.no_profile_widget)

        # stack 1: Auth View
        self.auth_view = None

        # stack 2: Dashboard View
        self.dashboard_view = None

        content_layout.addWidget(self.content_stack, stretch=1)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(content_frame, stretch=1)

        self._update_state()

    def _update_state(self) -> None:
        """Update the view state based on profile existence and runs."""
        profile = load_profile("profile.json")

        if (
            not profile
            or not profile.get("sessions")
            or len(profile.get("sessions", [])) < 1
        ):
            self.content_stack.setCurrentWidget(self.no_profile_widget)
            return

        if self.auth_view:
            self.content_stack.removeWidget(self.auth_view)
            self.auth_view.deleteLater()

        if self.dashboard_view:
            self.content_stack.removeWidget(self.dashboard_view)
            self.dashboard_view.deleteLater()
            self.dashboard_view = None

        self.auth_view = AuthView(profile)
        self.auth_view.auth_success.connect(self._on_auth_success)
        self.auth_view.auth_failed.connect(self._on_auth_failed)
        self.content_stack.addWidget(self.auth_view)
        self.content_stack.setCurrentWidget(self.auth_view)

    def _on_auth_success(self) -> None:
        """Handle successful authentication."""
        if not self.dashboard_view:
            self.dashboard_view = DashboardView()
            self.dashboard_view.exit_clicked.connect(self._update_state)
            self.content_stack.addWidget(self.dashboard_view)

        self.content_stack.setCurrentWidget(self.dashboard_view)

    def _on_auth_failed(self) -> None:
        """Handle failed authentication."""
        self.content_stack.setCurrentWidget(self.auth_view)
