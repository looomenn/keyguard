"""Utility functions."""

import sys
import json
import uuid
import time
import os

from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QFontDatabase

from pathlib import Path


def get_resource_path(relative_path: str | Path) -> Path:
    """
    Get the absolute path for a resource, compatible with PyInstaller.

    :param relative_path: Path relative to the project root.
    :return: Absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = Path(sys._MEIPASS) / 'keyguard'
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


def load_font() -> None:
    """Load custom font."""
    fonts_dir = get_resource_path("keyguard/resources/font")
    loaded = False
    for font_file in fonts_dir.iterdir():
        if font_file.suffix.lower() in {".ttf", ".otf"}:
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id < 0:
                print(f"⚠️ Failed to load font {font_file.name}")
                return
            families = QFontDatabase.applicationFontFamilies(font_id)
            loaded = True
    if loaded:
        print("✅ Fonts loaded successfully")


def load_profile(path: str) -> dict:
    abs_path = get_resource_path(path)
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_profile(profile: dict, path: str) -> None:
    abs_path = get_resource_path(path)
    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def delete_profile(path: str) -> bool:
    """
    Delete a profile file.
    
    :param path: Path to the profile file
    :return: True if deletion was successful, False otherwise
    """
    try:
        abs_path = get_resource_path(path)
        if abs_path.exists():
            os.remove(abs_path)
            return True
    except Exception as e:
        print(f"Error deleting profile: {e}")
    return False


def create_profile(phrase: str) -> dict:
    now = int(time.time())
    return {
        "uuid": str(uuid.uuid4()),
        "phrase": phrase,
        "total_runs": 0,
        "means": [],
        "variances": [],
        "sessions": [],
        "created": time.strftime("%Y-%m-%d %H:%M", time.localtime(now)),
        "updated": time.strftime("%Y-%m-%d %H:%M", time.localtime(now)),
    }


def generate_session_id() -> str:
    return str(uuid.uuid4())
