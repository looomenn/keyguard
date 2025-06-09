"""LabelValue component."""

from typing import ClassVar

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LabelValue(QWidget):
    """LabelValue component class."""

    SIZES: ClassVar[dict[str, str]] = {
        "small": "small",
        "medium": "medium",
        "large": "large",
    }

    def __init__(
        self,
        label: str,
        value: str,
        size: str = "medium",
        bold: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize LabelValue component.

        Args:
            label: the label to display
            value: the value to display
            size: the size of the label
            bold: whether to display the label in bold
            parent: the parent widget
        """
        super().__init__(parent)
        if size not in self.SIZES:
            size = "medium"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setProperty("class", f"label-value_label--{self.SIZES[size]}")
        layout.addWidget(lbl)

        val = QLabel(value)
        val.setProperty(
            "class",
            f"label-value_value--{self.SIZES[size]}" + (" bold" if bold else ""),
        )
        # enable rich text so we can inject <span> tags
        val.setTextFormat(Qt.TextFormat.RichText)
        # store raw value for later re-render
        val.setProperty("_raw_value", value)
        layout.addWidget(val)

        self.label_widget = lbl
        self.value_widget = val

    def set_value(self, value: str) -> None:
        """Set the value of the label.

        Args:
            value: the value to set
        """
        self.value_widget.setProperty("_raw_value", value)
        self.value_widget.setText(value)

    def highlight_match(self, matched: int, incorrect: int = 0) -> None:
        """Highlight the match in the value.

        Args:
            matched: number of leading characters to color as "correct"
            incorrect: number of characters to color as "incorrect" (after correct ones)
        """
        raw = self.value_widget.property("_raw_value") or ""

        correct = raw[:matched]
        wrong = raw[matched:incorrect] if incorrect > matched else ""
        rest = raw[incorrect:] if incorrect > matched else raw[matched:]

        html = (
            f'<span style="color: #69FF6E;">{correct}</span>'
            f'<span style="color: #f44336;">{wrong}</span>'
            f'<span style="color: #666;">{rest}</span>'
        )
        self.value_widget.setText(html)
