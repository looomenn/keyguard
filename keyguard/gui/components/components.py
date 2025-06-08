"""UI components with black and white theme."""

from PyQt6.QtWidgets import QLineEdit, QSpinBox, QPushButton
from PyQt6.QtCore import Qt

class LineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                border: 1px solid #333333;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007AFF;
                background-color: #000000;
            }
            QLineEdit:disabled {
                background-color: #000000;
                color: #666666;
                border-color: #333333;
            }
        """)

class SpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QSpinBox {
                background-color: #000000;
                border: 1px solid #333333;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QSpinBox:focus {
                border: 1px solid #007AFF;
                background-color: #000000;
            }
            QSpinBox:disabled {
                background-color: #000000;
                color: #666666;
                border-color: #333333;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #000000;
                border: 1px solid #333333;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #1A1A1A;
                border-color: #007AFF;
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background-color: #333333;
            }
        """)

class Button(QPushButton):
    def __init__(self, text: str, primary: bool = False, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#FFFFFF' if primary else '#000000'};
                color: {'#000000' if primary else '#FFFFFF'};
                border: 1px solid {'#FFFFFF' if primary else '#333333'};
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {'#F5F5F5' if primary else '#1A1A1A'};
                border-color: #007AFF;
            }}
            QPushButton:pressed {{
                background-color: {'#E5E5E5' if primary else '#333333'};
            }}
            QPushButton:disabled {{
                background-color: {'#CCCCCC' if primary else '#000000'};
                color: {'#666666' if primary else '#666666'};
                border-color: {'#CCCCCC' if primary else '#333333'};
            }}
            QPushButton:focus {{
                border: 1px solid #007AFF;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)