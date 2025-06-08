"""Training Frame."""

import json
import time
import statistics
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QSizePolicy, QLabel, QVBoxLayout,
    QStackedWidget, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QKeyEvent

from keyguard.utils import get_svg
from keyguard.gui.components.components import LineEdit, SpinBox, Button

class TrainingFrame(QWidget):
    back_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyguard — Тренування")
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)

        # Header
        header_frame = QFrame()
        header_frame.setProperty("class", "header-frame")
        header_frame.setStyleSheet("""
            QFrame[class~="header-frame"] {
                border: 1px solid #333333;
                background-color: #000000;
                border-bottom: 0px;
            }
        """)

        # Create left and right sections for header
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
        header_title.setStyleSheet("font-size: 24px; font-weight: 500; color: #FFFFFF; background-color: transparent;")

        # Add elements to left section
        header_left_layout.addWidget(back_btn)
        header_left_layout.addWidget(logo)
        header_left_layout.addWidget(header_title)
        header_left_layout.addStretch(1)

        # Add start button to right section
        self.start_btn = Button("Почати тренування", primary=True)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._start_training)
        header_right_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Combine left and right sections in header
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(0)
        header_layout.addWidget(header_left)
        header_layout.addWidget(header_right)

        # Content Stack
        self.content_stack = QStackedWidget()
        
        # Stack 0: No Profile
        no_profile_widget = QWidget()
        no_profile_layout = QVBoxLayout(no_profile_widget)
        no_profile_layout.setContentsMargins(24, 24, 24, 24)
        no_profile_layout.setSpacing(32)
        
        no_profile_label = QLabel("Профіль не знайдено. Почніть тренування, щоб створити профіль.")
        no_profile_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        no_profile_layout.addWidget(no_profile_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Stack 1: Profile Stats
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(24, 24, 24, 24)
        stats_layout.setSpacing(32)
        
        stats_card = QFrame()
        stats_card.setProperty("class", "stats-card")
        stats_card_layout = QVBoxLayout(stats_card)
        stats_card_layout.setContentsMargins(24, 24, 24, 24)
        stats_card_layout.setSpacing(16)
        
        self.phrase_label = QLabel()
        self.phrase_label.setStyleSheet("font-size: 18px; font-weight: 500;")
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-size: 14px;")
        
        reset_btn = Button("Скинути профіль", primary=True)
        reset_btn.clicked.connect(self._start_training)
        
        stats_card_layout.addWidget(self.phrase_label)
        stats_card_layout.addWidget(self.stats_label)
        stats_card_layout.addWidget(reset_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        stats_layout.addWidget(stats_card)
        
        # Stack 2: Training Screen
        training_widget = QWidget()
        training_layout = QVBoxLayout(training_widget)
        training_layout.setContentsMargins(24, 24, 24, 24)
        training_layout.setSpacing(32)
        
        phrase_container = QWidget()
        phrase_layout = QVBoxLayout(phrase_container)
        phrase_layout.setContentsMargins(0, 0, 0, 0)
        phrase_layout.setSpacing(8)
        
        phrase_title = QLabel("Ваша фраза:")
        phrase_title.setStyleSheet("font-size: 16px; font-weight: 500;")
        
        self.target_phrase = QLabel()
        self.target_phrase.setStyleSheet("font-size: 24px; font-weight: 500;")
        
        phrase_layout.addWidget(phrase_title)
        phrase_layout.addWidget(self.target_phrase)
        
        self.training_input = LineEdit()
        self.training_input.setPlaceholderText("Введіть фразу...")
        self.training_input.installEventFilter(self)
        self.training_input.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 16px;
            }
        """)
        
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("font-size: 14px; color: #666666;")
        
        training_layout.addWidget(phrase_container)
        training_layout.addWidget(self.training_input)
        training_layout.addWidget(self.progress_label)
        training_layout.addStretch(1)
        
        # Add all stacks
        self.content_stack.addWidget(no_profile_widget)
        self.content_stack.addWidget(stats_widget)
        self.content_stack.addWidget(training_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(header_frame)
        main_layout.addWidget(self.content_stack, stretch=1)
        
        # Initialize state
        self._phrase = ""
        self._expected_len = 0
        self._runs = []
        self._current_run = []
        self._collected = 0
        self._current_attempt = 0
        self._max_attempts = 20
        
        self._update_state()

    def _update_state(self):
        """Update the UI state based on profile existence."""
        profile = self._get_profile()
        if profile:
            self._phrase = profile["phrase"]
            self.phrase_label.setText(f"Фраза: {self._phrase}")
            
            # Format stats
            stats_text = "Статистика:\n"
            for i, (mean, std) in enumerate(zip(profile["means"], profile["stddevs"])):
                stats_text += f"Символ {i+1}: {mean:.1f}ms ± {std:.1f}ms\n"
            self.stats_label.setText(stats_text)
            
            self.content_stack.setCurrentIndex(1)  # Show stats
        else:
            self.content_stack.setCurrentIndex(0)  # Show no profile

    def _start_training(self):
        """Start a new training session."""
        self._runs = []
        self._current_run = []
        self._collected = 0
        self._current_attempt = 0
        
        self.target_phrase.setText(self._phrase)
        self.training_input.clear()
        self.training_input.setEnabled(True)
        self.training_input.setFocus()
        
        self._update_progress()
        self.content_stack.setCurrentIndex(2)  # Show training screen

    def _update_progress(self):
        """Update the progress label."""
        self.progress_label.setText(f"Спроба {self._current_attempt + 1} з {self._max_attempts}")

    def eventFilter(self, obj, event):
        if obj == self.training_input and event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            
            if key_event.key() == Qt.Key.Key_Escape:
                self._update_state()
                return True
                
            if key_event.key() == Qt.Key.Key_Return:
                current_text = self.training_input.text()
                if current_text == self._phrase:
                    self._current_attempt += 1
                    self._runs.append(self._current_run)
                    self._current_run = []
                    
                    if self._current_attempt >= self._max_attempts:
                        self._compute_and_save()
                    else:
                        self.training_input.clear()
                        self._update_progress()
                return True
                
            if key_event.text():
                self._current_run.append(time.time())
                return False
                
        return super().eventFilter(obj, event)

    def _compute_and_save(self):
        """Compute statistics and save the profile."""
        # transpose runs
        cols = list(zip(*self._runs))
        means = [statistics.mean(c) for c in cols]
        stddev = [max(statistics.pstdev(c), 1.0) for c in cols]
        
        # save profile
        profile = {
            "phrase": self._phrase,
            "means": means,
            "stddevs": stddev
        }
        
        if self._save_profile(profile):
            self._update_state()
        else:
            QMessageBox.warning(
                self, "Помилка",
                "Не вдалося зберегти профіль. Спробуйте ще раз."
            )

    def _get_profile(self):
        """Get the profile data."""
        try:
            path = Path("resources/profile.json")
            if not path.exists():
                return None
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _save_profile(self, profile):
        """Save the profile data."""
        try:
            path = Path("resources/profile.json")
            path.parent.mkdir(exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
