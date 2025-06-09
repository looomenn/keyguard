"""Utility functions."""

import json
import os
import sys
import time
import uuid
from pathlib import Path

from platformdirs import user_data_path
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QWidget


def get_resource_path(relative_path: str | Path) -> Path:
    """Get the absolute path for a resource, compatible with PyInstaller.

    Args:
        relative_path: Path relative to the project root.

    Returns:
        Absolute path to the resource.
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS) / "keyguard"
    else:
        base_path = Path(__file__).resolve().parent
    return base_path / relative_path


def get_user_data_dir(app_name: str = "Keyguard", app_author: str = "ange1o") -> Path:
    """Get the user data directory for the application.

    Args:
        app_name: The name of the application.
        app_author: The author of the application.

    Returns:
        The user data directory.
    """
    data_dir = user_data_path(appname=app_name, appauthor=app_author)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_svg(
    relative_path: str | Path,
    parent: QWidget | None = None,
    width: int | None = None,
    height: int | None = None,
) -> QSvgWidget:
    """Create a QSvgWidget from an SVG file located in resources.

    Optionally set fixed width/height to scale.

    Args:
        relative_path: Path inside resources folder
        parent: parent widget
        width: use as fixed width
        height: use as fixed height

    Returns:
        configured QSvgWidget
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
    """Load custom font.

    Returns:
        None
    """
    fonts_dir = get_resource_path("resources/font")
    loaded = False
    for font_file in fonts_dir.iterdir():
        if font_file.suffix.lower() in {".ttf", ".otf"}:
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id < 0:
                print(f"Failed to load font {font_file.name}")
                return
            loaded = True
    if loaded:
        print("✅ Fonts loaded successfully")


def load_profile(filename: str = "profile.json") -> dict:
    """Load a user profile from the user data directory.

    Args:
        filename: The name of the profile file.

    Returns:
        The profile data.
    """
    profile_dir = get_user_data_dir()
    profile_path = profile_dir / filename

    try:
        with open(profile_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Profile file not found at: {profile_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {profile_path}: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred loading profile from {profile_path}: {e}")
        return {}


def save_profile(profile: dict, filename: str = "profile.json") -> None:
    """Save a user profile to the user data directory.

    Args:
        profile: The profile data.
        filename: The name of the profile file.

    Returns:
        None
    """
    profile_dir = get_user_data_dir()
    profile_path = profile_dir / filename

    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        print(f"Profile saved successfully to: {profile_path}")
    except Exception as e:
        print(f"Error saving profile to {profile_path}: {e}")


def delete_profile(filename: str = "profile.json") -> bool:
    """Delete a profile file from the user data directory.

    Args:
        filename: The name of the profile file.

    Returns:
        bool: True if the profile was deleted, False otherwise.
    """
    profile_dir = get_user_data_dir()
    profile_path = profile_dir / filename
    try:
        if profile_path.exists():
            os.remove(profile_path)
            return True
        else:
            print(f"Profile file not found for deletion: {profile_path}")
            return True
    except Exception as e:
        print(f"Error deleting profile {profile_path}: {e}")
    return False


def create_profile(phrase: str) -> dict:
    """Create a new profile.

    Args:
        phrase: The phrase to use for the profile.

    Returns:
        The profile data.
    """
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
    """Generate a new session ID.

    Returns:
        The session ID.
    """
    return str(uuid.uuid4())
