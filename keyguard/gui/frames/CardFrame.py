"""Card Frame."""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget

from keyguard.utils import get_resource_path, get_svg


class CardFrame(QFrame):
    clicked = pyqtSignal()

    def __init__(self, title: str, image_path: str = None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setProperty("class", "card-frame")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QFrame[class~="card-frame"] {
                border: 1px solid #3c3c3c;
                background-color: #000000;
                text-align:left;
                padding: 24px
            }
            
            QFrame[class~="card-frame"]:hover {
                background-color: #1c1b1b;
            }
            
            QLabel {
                background: transparent;
                color: white;
                font-weight: 500;
                font-size: 22px;
            }

        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label = QLabel(title, self)
        label.setProperty("class", "card-title")
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(label)

        if image_path:
            rel_image_path = get_resource_path(image_path)

            svg_widget = get_svg(
                rel_image_path,
                self,
                width=150,
                height=150
            )
            layout.addWidget(svg_widget)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

