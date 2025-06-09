from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt

from keyguard.gui.components.components import Button


class ProfilePanel(QWidget):
    delete_clicked = pyqtSignal()

    def __init__(self, profile: dict, parent=None):
        super().__init__(parent)
        self.profile = profile
        layout = QVBoxLayout(self)
        self.setProperty("class", "profile-panel")

        title = QLabel("Поточний профіль")
        title.setProperty("class", "profile-panel_title")
        layout.addWidget(title)

        layout.addItem(QSpacerItem(20, 24, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum))

        def add_row(label, value):
            l = QLabel(label)
            l.setProperty("class", "profile-panel_label")
            v = QLabel(value)
            v.setProperty("class", "profile-panel_value")
            v.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addItem(QSpacerItem(20, 16, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum))
            layout.addWidget(l)
            layout.addWidget(v)

        add_row("USERID", str(profile.get("uuid", "N/A")))
        add_row("RUNS", str(profile.get("total_runs", "N/A")))
        add_row("Created", str(profile.get("created", "N/A")))
        add_row("Updated", str(profile.get("updated", "N/A")))

        avg_dwell = "N/A"
        means = profile.get("means")
        if means and isinstance(means, list) and len(means) > 0:
            avg_dwell = f"{sum(means)/len(means):.0f} ms"
        add_row("Avg Dwell", avg_dwell)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        delete_btn = Button("Видалити")
        delete_btn.setProperty("class", "btn")

        delete_btn.clicked.connect(self.delete_clicked.emit)
        layout.addWidget(delete_btn, alignment=Qt.AlignmentFlag.AlignBottom) 
