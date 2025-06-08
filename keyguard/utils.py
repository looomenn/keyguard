"""Utility functions."""

import sys

from PyQt6.QtSvgWidgets import QSvgWidget

from pathlib import Path


def get_resource_path(relative_path: str | Path) -> Path:
    """
    Get the absolute path for a resource, compatible with PyInstaller.

    :param relative_path: Path relative to the project root.
    :return: Absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) / 'keyguardtest'
    else:
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path


def get_svg(
        relative_path: str | Path,
        parent=None,
        width: int = None,
        height: int = None
) -> QSvgWidget:
    """
    Create a QSvgWidget from an SVG file located in resources.
    Optionally set fixed width/height to scale.

    :param relative_path: Path inside resources folder
    :param parent: parent widget
    :param width: use as fixed width
    :param height: use as fixed height
    :return: configured QSvgWidget
    """
    path = get_resource_path(relative_path)
    svg = QSvgWidget(str(path), parent=parent)

    if width is not None:
        svg.setFixedWidth(width)

    if height is not None:
        svg.setFixedHeight(height)

    if width and height is not None:
        svg.setMaximumSize(width, height)

    svg.setStyleSheet("background-color: transparent")

    return svg
