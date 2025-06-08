"""Keyring manager for secure profile storage."""

import json
import keyring
from typing import Optional, Dict, Any

class KeyringManager:
    """Manages secure storage of profile data using system keyring."""

    SERVICE_NAME = "keyguard"
    PROFILE_KEY = "profile"

    @classmethod
    def has_profile(cls) -> bool:
        """Check if a profile exists in the keyring."""
        try:
            return keyring.get_password(cls.SERVICE_NAME, cls.PROFILE_KEY) is not None
        except Exception:
            return False

    @classmethod
    def get_profile(cls) -> Optional[Dict[str, Any]]:
        """Get the profile data from keyring."""
        try:
            data = keyring.get_password(cls.SERVICE_NAME, cls.PROFILE_KEY)
            return json.loads(data) if data else None
        except Exception:
            return None

    @classmethod
    def save_profile(cls, profile: Dict[str, Any]) -> bool:
        """Save the profile data to keyring."""
        try:
            keyring.set_password(cls.SERVICE_NAME, cls.PROFILE_KEY, json.dumps(profile))
            return True
        except Exception:
            return False
