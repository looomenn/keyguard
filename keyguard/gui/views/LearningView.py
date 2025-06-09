import uuid
import time
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from keyguard.gui.components.components import Button, LineEdit, ProgressBar
from keyguard.gui.components.LabelValue import LabelValue
from keyguard.logic import remove_outliers_per_position, compute_session_stats
from keyguard.utils import delete_profile, get_resource_path


class LearningView(QWidget):
    session_complete = pyqtSignal(dict)
    session_cancelled = pyqtSignal()
    state_changed = pyqtSignal(int)  # Signal to switch states

    def __init__(self, phrase, profile=None, parent=None):
        super().__init__(parent)
        self.phrase = phrase
        self.profile = profile or {}
        self.profile_path = get_resource_path("keyguard/profiles/profile.json")
        self.max_runs = 2
        self.max_mistakes = 3
        self.current_run = 0
        self.mistakes = 0
        self.timestamps = []
        self.session_runs = []
        self.session_start_ts = int(time.time())
        self.accepted_runs = 0
        self.session_id = str(uuid.uuid4())[:8]

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(40)

        # Left: Session collector
        session_frame = QFrame()
        session_frame.setProperty("class", "session-frame")
        session_layout = QVBoxLayout(session_frame)
        session_layout.setSpacing(24)
        session_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Center container for session content
        session_content = QWidget()
        session_content_layout = QVBoxLayout(session_content)
        session_content_layout.setContentsMargins(40, 0, 0, 0)
        session_content_layout.setSpacing(24)
        session_content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Container for phrase and session ID in one row
        phrase_container = QWidget()
        phrase_container.setProperty("class", "phrase-container")
        phrase_layout = QHBoxLayout(phrase_container)
        phrase_layout.setContentsMargins(0, 0, 0, 0)
        phrase_layout.setSpacing(24)
        
        self.phrase_label = LabelValue("Фраза", str(self.phrase), size="large", bold=True)
        self.session_id_label = LabelValue("Session ID", self.session_id, size="large")
        
        phrase_layout.addWidget(self.session_id_label)
        phrase_layout.addWidget(self.phrase_label)
        phrase_layout.addStretch(1)
        
        session_content_layout.addWidget(phrase_container)

        # Container for input to control its width
        input_container = QWidget()
        input_container.setProperty("class", "input-container")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)
        self.input = LineEdit()
        self.input.setMinimumHeight(60)
        self.input.setPlaceholderText("Введіть фразу.")
        self.input.installEventFilter(self)
        input_layout.addWidget(self.input)
        session_content_layout.addWidget(input_container)

        # Container for progress to control its width
        progress_container = QWidget()
        progress_container.setProperty("class", "progress-container")
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(0)
        self.progress = ProgressBar()
        self.progress.setRange(0, self.max_runs)
        self.progress.setValue(0)
        progress_layout.addWidget(self.progress)
        session_content_layout.addWidget(progress_container)

        # Container for hint to control its width
        hint_container = QWidget()
        hint_container.setProperty("class", "hint-container")
        hint_layout = QVBoxLayout(hint_container)
        hint_layout.setContentsMargins(0, 0, 0, 0)
        hint_layout.setSpacing(0)
        self.hint = QLabel()
        self.hint.setStyleSheet("color:#f55; font-size:14px;")
        hint_layout.addWidget(self.hint, alignment=Qt.AlignmentFlag.AlignCenter)
        session_content_layout.addWidget(hint_container)

        # Container for cancel button to control its width
        button_container = QWidget()
        button_container.setProperty("class", "button-container")
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        cancel = Button("Зупинити тренування")
        cancel.clicked.connect(self.session_cancelled.emit)
        button_layout.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignCenter)
        session_content_layout.addWidget(button_container)

        session_layout.addWidget(session_content)
        main_layout.addWidget(session_frame, stretch=3)

        # Right: Profile info
        profile_frame = QFrame()
        profile_frame.setProperty("class", "profile-panel")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setContentsMargins(24, 24, 24, 24)
        profile_layout.setSpacing(24)

        title = QLabel("Поточний профіль")
        title.setProperty("class", "profile-panel_title")
        profile_layout.addWidget(title)

        # Create profile info rows using LabelValue
        self.profile_labels = {}
        self.profile_labels["USERID"] = LabelValue("USERID", str(self.profile.get("uuid", "N/A")), size="medium", bold=True)
        self.profile_labels["Created"] = LabelValue("Created", str(self.profile.get("created", "N/A")), size="medium")
        self.profile_labels["Updated"] = LabelValue("Updated", str(self.profile.get("updated", "N/A")), size="medium")
        self.profile_labels["RUNS"] = LabelValue("Total runs", str(self.profile.get("total_runs", "N/A")), size="medium", bold=True)
        
        avg_dwell = "N/A"
        means = self.profile.get("means")
        if means and isinstance(means, list) and len(means) > 0:
            avg_dwell = f"{sum(means)/len(means):.0f} ms"
        self.profile_labels["Avg Dwell"] = LabelValue("Avg Dwell", avg_dwell, size="medium", bold=True)

        # Add all profile labels to layout
        for label in self.profile_labels.values():
            profile_layout.addWidget(label)

        profile_layout.addStretch(1)

        delete_btn = Button("Видалити")
        # Check if profile file exists and disable button if it doesn't
        profile_exists = os.path.exists(self.profile_path)
        delete_btn.setEnabled(profile_exists)
        delete_btn.clicked.connect(self._on_delete_profile)
        profile_layout.addWidget(delete_btn, alignment=Qt.AlignmentFlag.AlignBottom)

        main_layout.addWidget(profile_frame, stretch=1)

    def eventFilter(self, obj, event):
        if obj is self.input:
            if event.type() == QEvent.Type.KeyPress:
                self._press_ts = time.perf_counter()
                return False

            if event.type() == QEvent.Type.KeyRelease:
                char = event.text()
                rel_ts = time.perf_counter()

                # if user pressed Enter
                if event.key() == Qt.Key.Key_Return:
                    entered = self.input.text()
                    if entered == self.phrase:
                        # compute dwell-times for this run
                        dwells = [ (r-p)*1000 for (p,r) in self.timestamps ]
                        self.session_runs.append(dwells)
                        self.accepted_runs += 1
                        self.current_run += 1
                        self.progress.setValue(self.current_run)
                        self.input.clear()
                        self.hint.clear()
                        # Reset highlighting
                        self.phrase_label.highlight_match(0)
                        if self.current_run >= self.max_runs:
                            self._finish_session()
                        else:
                            self.timestamps.clear()
                        return True
                    else:
                        self.mistakes += 1
                        self.hint.setText("Невірний текст, спробуйте знову")
                        self.input.clear()
                        self.timestamps.clear()
                        # Reset highlighting
                        self.phrase_label.highlight_match(0)
                        if self.mistakes > self.max_mistakes:
                            self.hint.setText("Забагато помилок. Починаємо спочатку.")
                            self._reset_session()
                        return True

                if char:
                    self.timestamps.append((self._press_ts, rel_ts))
                    # Update character highlighting
                    current_text = self.input.text()
                    matched = 0
                    incorrect = 0
                    for i, (typed, expected) in enumerate(zip(current_text, self.phrase)):
                        if typed == expected:
                            matched = i + 1
                        else:
                            incorrect = i + 1
                            break
                    self.phrase_label.highlight_match(matched, incorrect)
                    return True

        return super().eventFilter(obj, event)

    def _reset_session(self):
        self.current_run = 0
        self.mistakes = 0
        self.session_runs.clear()
        self.timestamps = []
        self.progress.setValue(0)
        # Reset highlighting
        self.phrase_label.highlight_match(0)

    def _finish_session(self):
        # remove outliers per character position
        cleaned = remove_outliers_per_position(self.session_runs)
        # compute session stats
        mean_s, std_s, _ = compute_session_stats(cleaned)
        session = {
            "id": self.session_id,
            "phrase": self.phrase,
            "timestamp": self.session_start_ts,
            "runs_count": self.current_run,
            "accepted_runs": self.accepted_runs,
            "runs": cleaned,
            "mean_session": mean_s,
            "stddev_session": std_s
        }
        self.session_complete.emit(session)

    def _on_delete_profile(self):
        """Handle profile deletion and switch to state 0."""
        if delete_profile(self.profile_path):
            self.state_changed.emit(0)  # Switch to state 0 after successful deletion 