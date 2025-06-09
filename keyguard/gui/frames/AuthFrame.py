from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

from keyguard.gui.components.components import Button
from keyguard.utils import get_svg, load_profile
from keyguard.gui.views.NoProfile import NoProfile
from keyguard.gui.views.AuthView import AuthView

class AuthFrame(QWidget):
    """Frame for authentication view."""
    back_clicked = pyqtSignal()
    switch_to_training = pyqtSignal()  # Signal to switch to training frame
    auth_success = pyqtSignal()  # Signal when authentication is successful

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyguard — Авторизація")

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

        logo = get_svg("keyguard/resources/locker.svg", self, width=32, height=32)

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
        self.no_profile_widget = NoProfile(mode="auth")
        self.no_profile_widget.start_training.connect(self.switch_to_training.emit)
        self.content_stack.addWidget(self.no_profile_widget)
        
        # Stack 1: Auth View
        self.auth_view = None
        
        content_layout.addWidget(self.content_stack, stretch=1)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(header_frame)
        self.main_layout.addWidget(content_frame, stretch=1)
        
        self._update_state()

    def _update_state(self):
        """Update the view state based on profile existence and runs."""
        profile = load_profile("keyguard/resources/profile.json")
        
        # Show no profile widget if:
        # 1. No profile exists
        # 2. Profile exists but has no sessions
        # 3. Profile has less than 20 sessions
        if not profile or not profile.get("sessions") or len(profile.get("sessions", [])) < 1:
            self.content_stack.setCurrentWidget(self.no_profile_widget)
            return
            
        # Show auth view if profile has enough sessions
        if self.auth_view:
            self.content_stack.removeWidget(self.auth_view)
            self.auth_view.deleteLater()
            
        self.auth_view = AuthView(profile)
        self.auth_view.auth_success.connect(self._on_auth_success)
        self.auth_view.auth_failed.connect(self._on_auth_failed)
        self.content_stack.addWidget(self.auth_view)
        self.content_stack.setCurrentWidget(self.auth_view)

    def _on_auth_success(self):
        """Handle successful authentication."""
        # TODO: Switch to main app view
        print("Authentication successful!")

    def _on_auth_failed(self):
        """Handle failed authentication."""
        # TODO: Show error message
        print("Authentication failed!")
