import os
import time
import uuid

import numpy as np
from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from keyguard.gui.components.components import Button, LineEdit, ProgressBar
from keyguard.gui.components.LabelValue import LabelValue
from keyguard.logic import compute_session_stats, remove_outliers_per_position
from keyguard.utils import delete_profile, get_resource_path


class LearningView(QWidget):
    """LearningView class."""

    session_complete = pyqtSignal(dict)
    session_cancelled = pyqtSignal()
    state_changed = pyqtSignal(int)
    show_stats = pyqtSignal(dict)
    back_clicked = pyqtSignal()

    def __init__(
        self,
        phrase: str,
        profile: dict | None = None,
        parent: QWidget | None = None,
        show_panel: bool = True,
    ) -> None:
        """Initialize LearningView.

        Args:
            phrase: the phrase to learn
            profile: the profile data
            parent: the parent widget
            show_panel: whether to show the profile panel
        """
        super().__init__(parent)
        self.phrase = phrase
        self.profile = profile or {}
        self.profile_path = get_resource_path("resources/profile.json")
        self.max_runs = 4
        self.max_mistakes = 3
        self.current_run = 0
        self.mistakes = 0
        self.timestamps = []
        self.session_runs = []
        self.session_start_ts = int(time.time())
        self.accepted_runs = 0
        self.session_id = str(uuid.uuid4())[:8]

        self.show_stats.connect(self._on_session_complete)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(40)

        session_frame = QFrame()
        session_frame.setProperty("class", "session-frame")
        session_layout = QVBoxLayout(session_frame)
        session_layout.setSpacing(24)
        session_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        session_content = QWidget()
        session_content_layout = QVBoxLayout(session_content)
        session_content_layout.setContentsMargins(
            40, 0, 0, 0
        ) if show_panel else session_content_layout.setContentsMargins(40, 0, 40, 0)
        session_content_layout.setSpacing(24)
        session_content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        phrase_container = QWidget()
        phrase_container.setProperty("class", "phrase-container")
        phrase_layout = QHBoxLayout(phrase_container)
        phrase_layout.setContentsMargins(0, 0, 0, 0)
        phrase_layout.setSpacing(24)

        self.phrase_label = LabelValue(
            "Фраза", str(self.phrase), size="large", bold=True
        )
        self.session_id_label = LabelValue("Session ID", self.session_id, size="large")

        phrase_layout.addWidget(self.session_id_label)
        phrase_layout.addWidget(self.phrase_label)
        phrase_layout.addStretch(1)

        session_content_layout.addWidget(phrase_container)

        input_container = QWidget()
        input_container.setProperty("class", "input-container")
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)

        self.input = LineEdit()
        self.input.setMinimumHeight(60)
        self.input.setPlaceholderText("Введіть фразу.")
        self.input.installEventFilter(self)
        self.input.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.input.installEventFilter(self)

        input_layout.addWidget(self.input)
        session_content_layout.addWidget(input_container)

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

        hint_container = QWidget()
        hint_container.setProperty("class", "hint-container")
        hint_layout = QVBoxLayout(hint_container)
        hint_layout.setContentsMargins(0, 0, 0, 0)
        hint_layout.setSpacing(0)
        self.hint = QLabel()
        self.hint.setStyleSheet("color:#f55; font-size:14px;")
        hint_layout.addWidget(self.hint, alignment=Qt.AlignmentFlag.AlignCenter)
        session_content_layout.addWidget(hint_container)

        button_container = QWidget()
        button_container.setProperty("class", "button-container")
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        cancel = Button("Нова сесія")
        cancel.clicked.connect(self.session_cancelled.emit)
        button_layout.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignLeft)

        if show_panel:
            session_content_layout.addWidget(button_container)

        session_layout.addWidget(session_content)
        main_layout.addWidget(session_frame, stretch=3)
        if show_panel:
            profile_frame = QFrame()
            profile_frame.setProperty("class", "profile-panel")
            profile_layout = QVBoxLayout(profile_frame)
            profile_layout.setContentsMargins(24, 24, 24, 24)
            profile_layout.setSpacing(24)

            title = QLabel("Поточний профіль")
            title.setProperty("class", "profile-panel_title")
            profile_layout.addWidget(title)

            self.profile_labels = {}
            self.profile_labels["USERID"] = LabelValue(
                "USERID", str(self.profile.get("uuid", "N/A")), size="medium", bold=True
            )
            self.profile_labels["Created"] = LabelValue(
                "Created", str(self.profile.get("created", "N/A")), size="medium"
            )
            self.profile_labels["Updated"] = LabelValue(
                "Updated", str(self.profile.get("updated", "N/A")), size="medium"
            )
            self.profile_labels["RUNS"] = LabelValue(
                "Total runs",
                str(self.profile.get("total_runs", "N/A")),
                size="medium",
                bold=True,
            )

            avg_dwell = "N/A"
            means = self.profile.get("means")
            if means and isinstance(means, list) and len(means) > 0:
                avg_dwell = f"{sum(means) / len(means):.0f} ms"
            self.profile_labels["Avg Dwell"] = LabelValue(
                "Avg Dwell", avg_dwell, size="medium", bold=True
            )

            for label in self.profile_labels.values():
                profile_layout.addWidget(label)

            profile_layout.addStretch(1)

            delete_btn = Button("Видалити")

            self._update_delete_button()
            delete_btn.clicked.connect(self._on_delete_profile)
            profile_layout.addWidget(delete_btn, alignment=Qt.AlignmentFlag.AlignBottom)

            main_layout.addWidget(profile_frame, stretch=1)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Handle events for the input widget.

        Args:
            obj: the object that sent the event
            event: the event

        Returns:
            bool: whether the event was handled
        """
        if obj is self.input:
            if event.type() == QEvent.Type.KeyPress:
                self._press_ts = time.perf_counter()
                return False

            if event.type() == QEvent.Type.KeyRelease:
                char = event.text()
                rel_ts = time.perf_counter()

                if event.key() == Qt.Key.Key_Return:
                    entered = self.input.text()
                    if entered == self.phrase:
                        # compute dwell-times for this run
                        dwells = [(r - p) * 1000 for (p, r) in self.timestamps]
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

                if char and len(self.timestamps) < len(self.phrase):
                    pos = len(self.timestamps)
                    correct = self.phrase[pos]

                    if char == correct:
                        self.timestamps.append((self._press_ts, rel_ts))
                        matched = pos + 1
                        incorrect = 0
                    else:
                        self.mistakes += 1
                        matched = pos
                        incorrect = pos + 1
                        self.hint.setText("Невірний текст, спробуйте знову")
                        self.input.clear()
                        self.timestamps.clear()

                    self.phrase_label.highlight_match(matched, incorrect)

        return super().eventFilter(obj, event)

    def _reset_session(self) -> None:
        """Reset the session."""
        self.current_run = 0
        self.mistakes = 0
        self.session_runs.clear()
        self.timestamps = []
        self.progress.setValue(0)
        self.phrase_label.highlight_match(0)

    def _finish_session(self) -> None:
        """Finish the session."""
        cleaned = remove_outliers_per_position(self.session_runs)
        mean_s, std_s, _ = compute_session_stats(cleaned)
        session = {
            "session_id": self.session_id,
            "phrase": self.phrase,
            "timestamp": self.session_start_ts,
            "total_runs": self.current_run,
            "accepted_runs": self.accepted_runs,
            "runs": cleaned,
            "mean": mean_s,
            "stddev": std_s,
        }
        self.session_complete.emit(session)
        self.show_stats.emit(session)

    def _on_profile_created(self) -> None:
        """Update UI when profile is created."""
        print("asdasd")
        if hasattr(self, "delete_btn"):
            self.delete_btn.setEnabled(True)

    def _update_delete_button(self) -> None:
        """Update delete button state based on profile existence."""
        if hasattr(self, "delete_btn"):
            self.delete_btn.setEnabled(os.path.exists(self.profile_path))

    def _on_delete_profile(self) -> None:
        """Handle profile deletion."""
        if delete_profile(self.profile_path):
            self.state_changed.emit(0)

    def _on_stats_back(self) -> None:
        """Handle stats back."""
        self.content_stack.setCurrentIndex(0)

    def _on_session_complete(self, session: dict) -> None:
        """Handle session completion."""
        # Compute statistics
        if session.get("runs"):
            dwells = session["runs"][0]
            session["mean"] = np.mean(dwells)
            session["std"] = np.std(dwells)

        self.session_cancelled.emit()
