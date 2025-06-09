# keyguard/gui/views/AuthView.py

import math
from PyQt6.QtCore    import pyqtSignal, QEvent, Qt
from PyQt6.QtGui     import QKeySequence, QKeyEvent
from keyguard.gui.views.LearningView import LearningView
from keyguard.logic   import calculate_authentication_delta
import numpy as np

class AuthView(LearningView):
    """View for authentication using typing pattern."""
    auth_success = pyqtSignal()
    auth_failed  = pyqtSignal()

    def __init__(self, profile, parent=None):
        super().__init__(phrase=profile.get("phrase", ""), profile=profile, parent=parent, show_panel=False)
        self.attempts = 1
        self.max_attempts = 1

        self.profile_stats = self._get_profile_stats()

    def _get_profile_stats(self):
        """Compute per-position mean and variance from all saved runs."""
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
            return None

        try:
            arr = np.array(all_dwells, dtype=float)
            means = arr.mean(axis=0).tolist()
            vars  = arr.var(axis=0).tolist()
        except Exception:
            # Fallback pure Python
            cols = list(zip(*all_dwells))
            means = [sum(col)/len(col) for col in cols]
            vars  = [sum((x - m)**2 for x in col)/len(col) for col, m in zip(cols, means)]

        return {"means": means, "variances": vars}


    def _on_session_complete(self, session: dict):
        """Handle a single authentication attempt."""
        runs = session.get("runs", [])
        stats = self.profile_stats
        if not runs or not stats:
            self.auth_failed.emit()
            return

        actual = runs[0]  # first (and only) run
        if not actual:
            self.auth_failed.emit()
            return

        means = stats["means"]
        variances = stats["variances"]

        deltas, thresholds, ok_flags = calculate_authentication_delta(
            actual, means, variances, threshold_factor=2.0
        )

        print("DELTAS:", deltas)
        print("THRESHOLDS:", thresholds)
        print("OK FLAGS:", ok_flags)

        if all(ok_flags):
            self.auth_success.emit()
            print("Auth success")
        else:
            self.attempts += 1
            if self.attempts >= self.max_attempts:
                self.auth_failed.emit()
                print("Auth failed: Max attempts reached")
            else:
                print("Auth failed: Attempt", self.attempts)
                self._reset_session()
