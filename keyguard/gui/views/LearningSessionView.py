import uuid
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton
)
from PyQt6.QtCore    import Qt, pyqtSignal, QEvent
from keyguard.logic   import remove_outliers_per_position, compute_session_stats

class LearningSessionView(QWidget):
    session_complete  = pyqtSignal(dict)
    session_cancelled = pyqtSignal()

    def __init__(self, phrase, max_runs=20, max_mistakes=3, parent=None):
        super().__init__(parent)
        self.phrase            = phrase
        self.max_runs          = max_runs
        self.max_mistakes      = max_mistakes
        self.current_run       = 0
        self.mistakes          = 0
        self.timestamps        = []     # list of (press, release) tuples
        self.session_runs      = []     # list of raw dwell-time lists
        self.session_start_ts  = int(time.time())
        self.accepted_runs     = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32,32,32,32)
        layout.setSpacing(24)

        self.phrase_label = QLabel(f"Фраза: {self.phrase}")
        self.phrase_label.setStyleSheet("font-size:16px; color:#fff;")
        layout.addWidget(self.phrase_label)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Введіть фразу.")
        self.input.installEventFilter(self)
        layout.addWidget(self.input)

        self.progress = QProgressBar()
        self.progress.setRange(0, self.max_runs)
        self.progress.setValue(0)
        self.progress.setFormat("%p%")
        layout.addWidget(self.progress)

        self.hint = QLabel()
        self.hint.setStyleSheet("color:#f55; font-size:14px;")
        layout.addWidget(self.hint)

        cancel = QPushButton("Вийти")
        cancel.clicked.connect(self.session_cancelled.emit)
        layout.addWidget(cancel, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addStretch(1)

    def eventFilter(self, obj, event):
        if obj is self.input:
            if event.type() == QEvent.Type.KeyPress:
                self._press_ts = time.perf_counter()
                return False

            if event.type() == QEvent.Type.KeyRelease:
                char = event.text()
                rel_ts = time.perf_counter()
                # record only real characters
                if char:
                    self.timestamps.append((self._press_ts, rel_ts))
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
                        if self.mistakes > self.max_mistakes:
                            self.hint.setText("Забагато помилок. Починаємо спочатку.")
                            self._reset_session()
                        return True
        return super().eventFilter(obj, event)

    def _reset_session(self):
        self.current_run  = 0
        self.mistakes     = 0
        self.session_runs.clear()
        self.translates = []
        self.progress.setValue(0)

    def _finish_session(self):
        # remove outliers per character position
        cleaned = remove_outliers_per_position(self.session_runs)
        # compute session stats
        mean_s, std_s, _ = compute_session_stats(cleaned)
        session = {
            "id":            str(uuid.uuid4()),
            "phrase":        self.phrase,
            "timestamp":     self.session_start_ts,
            "runs_count":    self.current_run,
            "accepted_runs": self.accepted_runs,
            "runs":          cleaned,
            "mean_session":  mean_s,
            "stddev_session": std_s
        }
        self.session_complete.emit(session)
