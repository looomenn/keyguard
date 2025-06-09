# keyguard/gui/views/AuthView.py

import numpy as np
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget

from keyguard.gui.views.LearningView import LearningView
from keyguard.logic import calculate_authentication_delta


class AuthView(LearningView):
    """View for authentication using typing pattern."""

    auth_success = pyqtSignal()
    auth_failed = pyqtSignal()

    def __init__(self, profile: dict, parent: QWidget | None = None) -> None:
        """Initialize AuthView.

        Args:
            profile: the profile data
            parent: the parent widget
        """
        super().__init__(
            phrase=profile.get("phrase", ""),
            profile=profile,
            parent=parent,
            show_panel=False,
        )
        self.attempts = 1
        self.max_attempts = 1

        self.profile_stats = self._get_profile_stats()

    def _get_profile_stats(self) -> dict:
        """Compute per-position mean and variance from all saved runs.

        Returns:
            dict: the profile statistics
        """
        profile = self.profile or {}
        sessions = profile.get("sessions", [])
        phrase_len = len(profile.get("phrase", ""))

        all_dwells = []
        for sess in sessions:
            for run in sess.get("runs", []):
                print("RUN:", run)
                print("RUN TYPE:", type(run))
                print("RUN LENGTH:", len(run))
                print("PHRASE LENGTH:", phrase_len)
                if isinstance(run, list) and len(run) == phrase_len:
                    all_dwells.append(run)

        if not all_dwells:
            return {"means": [], "variances": []}

        try:
            arr = np.array(all_dwells)
            means = arr.mean(axis=0).tolist()
            variances = arr.var(axis=0, ddof=1).tolist()
        except Exception:
            cols = list(zip(*all_dwells, strict=False))
            means = [sum(col) / len(col) for col in cols]
            variances = [
                sum((x - m) ** 2 for x in col) / (len(col) - 1)
                for col, m in zip(cols, means, strict=False)
            ]

        return {"means": means, "variances": variances}

    def _on_session_complete(self, session: dict) -> None:
        """Handle a single authentication attempt.

        Args:
            session: the session data
        """
        runs = session.get("runs", [])
        stats = self.profile_stats
        if not runs or not stats:
            self.auth_failed.emit()
            return

        actual = runs[0]
        if not actual:
            self.auth_failed.emit()
            return

        means = stats["means"]
        variances = stats["variances"]

        deltas, thresholds, ok_flags = calculate_authentication_delta(
            actual, means, variances, threshold_factor=2.5
        )

        print("DELTAS:", deltas)
        print("THRESHOLDS:", thresholds)
        print("OK FLAGS:", ok_flags)

        if all(ok_flags):
            self.auth_success.emit()
            print("Auth success")
        else:
            self.attempts += 1
            print("Auth failed: Attempt", self.attempts)
            self._reset_session()

            if self.attempts >= self.max_attempts:
                self.auth_failed.emit()
                print("Auth failed: Max attempts reached")
                self._reset_session()
