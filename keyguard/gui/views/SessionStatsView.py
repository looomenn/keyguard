from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from keyguard.gui.components.components import Button
from keyguard.gui.components.LabelValue import LabelValue

class SessionStatsView(QWidget):
    """View for displaying session statistics."""
    back_clicked = pyqtSignal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Title
        title = QLabel("Статистика сесії")
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        # Stats container
        stats_frame = QFrame()
        stats_frame.setProperty("class", "stats-frame")
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setSpacing(16)
        
        # Add session info
        self.stats_labels = {}
        self.stats_labels["session_id"] = LabelValue("Session ID", str(self.session.get("session_id", "N/A")), size="medium")
        self.stats_labels["phrase"] = LabelValue("Phrase", str(self.session.get("phrase", "N/A")), size="medium")
        self.stats_labels["total_runs"] = LabelValue("Total Runs", str(self.session.get("total_runs", "N/A")), size="medium")
        self.stats_labels["accepted_runs"] = LabelValue("Accepted Runs", str(self.session.get("accepted_runs", "N/A")), size="medium")
        self.stats_labels["mean"] = LabelValue("Average Dwell Time", f"{self.session.get('mean', 0):.2f} ms", size="medium")
        self.stats_labels["stddev"] = LabelValue("Standard Deviation", f"{self.session.get('stddev', 0):.2f} ms", size="medium")
        
        for label in self.stats_labels.values():
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_frame)
        layout.addStretch(1)
        
        # Back button
        back_btn = Button("Повернутися назад")
        back_btn.clicked.connect(self.back_clicked.emit)
        
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignBottom)
        
    def update_display(self):
        """Update the display with current session data."""
        self.stats_labels["session_id"].set_value(str(self.session.get("session_id", "N/A")))
        self.stats_labels["phrase"].set_value(str(self.session.get("phrase", "N/A")))
        self.stats_labels["total_runs"].set_value(str(self.session.get("total_runs", "N/A")))
        self.stats_labels["accepted_runs"].set_value(str(self.session.get("accepted_runs", "N/A")))
        self.stats_labels["mean"].set_value(f"{self.session.get('mean', 0):.2f} ms")
        self.stats_labels["stddev"].set_value(f"{self.session.get('stddev', 0):.2f} ms") 
