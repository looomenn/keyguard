"""Logic module."""


import statistics
from typing import Any, List
import math
from scipy.stats import t as t_dist, f as f_dist


def compute_session_stats(runs: list[list[float]]) -> tuple[float, float, list[list[float]]]:
    """
    Given a list of dwell-time runs (each run is a list of floats for each character),
    compute per-run means, per-run stddev, and also return the raw runs.

    Returns:
      (mean_session, stddev_session, runs)
    """
    flat = [value for run in runs for value in run]
    mean_session = statistics.mean(flat)
    stddev_session = max(statistics.pstdev(flat), 1.0)
    return mean_session, stddev_session, runs


def update_aggregate_profile(profile: dict[str, Any], session: dict[str, Any]) -> None:
    """
    Incrementally update profile['means'] and profile['variances'] with the new session data,
    and bump profile['total_runs'].

    Profile fields used:
      profile["means"]: List[float]
      profile["variances"]: List[float]  (population variance)
      profile["total_runs"]: int

    Session fields required:
      session["runs"]: List[List[float]]  (accepted dwell runs)
      session["runs_count"]: int          (number of runs in this session)
    """
    new_runs = session["runs"]
    num_new = len(new_runs)
    if num_new == 0:
        return

    # Обчислюємо середні та дисперсії по позиціях для цієї сесії
    cols = list(zip(*new_runs))  # транспонуємо: по символах
    session_means = [statistics.mean(c) for c in cols]
    session_vars  = [statistics.pstdev(c) ** 2 for c in cols]  # дисперсія

    # Якщо це перша сесія — просто записуємо
    if profile.get("total_runs", 0) == 0 or not profile.get("means"):
        profile["means"]     = session_means
        profile["variances"] = session_vars
        profile["total_runs"] = num_new
        return

    # Інакше — інкрементальне оновлення (пулінг)
    old_means = profile["means"]
    old_vars = profile["variances"]
    old_n = profile["total_runs"]

    updated_means = []
    updated_vars  = []
    for i, (m_old, v_old, m_s, v_s) in enumerate(zip(old_means, old_vars, session_means, session_vars)):
        # нове середнє = (m_old*old_n + m_s*num_new) / (old_n + num_new)
        total_n = old_n + num_new
        m_new = (m_old * old_n + m_s * num_new) / total_n

        # нова дисперсія (пулінг)
        # σ²_new = [v_old*old_n + v_s*num_new + (m_old - m_s)² * (old_n*num_new/total_n)] / total_n
        delta = m_old - m_s
        pooled = (v_old * old_n + v_s * num_new + (delta * delta) * (old_n * num_new / total_n))
        v_new = pooled / total_n

        updated_means.append(m_new)
        updated_vars.append(v_new)

    profile["means"]     = updated_means
    profile["variances"] = updated_vars
    profile["total_runs"] = total_n


def rebuild_profile_from_history(profile: dict[str, Any]) -> None:
    """
    Completely recompute profile['means'], ['variances'], and ['total_runs']
    by pooling ALL runs in profile['sessions'].

    Useful for a periodic "rebase" after many sessions.
    """
    all_runs = []
    for sess in profile.get("sessions", []):
        all_runs.extend(sess.get("runs", []))
    if not all_runs:
        profile["means"] = []
        profile["variances"] = []
        profile["total_runs"] = 0
        return

    cols = list(zip(*all_runs))
    profile["means"] = [statistics.mean(c) for c in cols]
    profile["variances"] = [statistics.pstdev(c) ** 2 for c in cols]
    profile["total_runs"] = len(all_runs)


def calculate_authentication_delta(
    actual: list[float],
    means: list[float],
    variances: list[float],
    threshold_factor: float = 2.0
) -> tuple[list[float], list[float], list[bool]]:
    """
    For a single candidate run, compute the absolute errors, per-position thresholds,
    and a True/False flag for each whether abs(actual - mean) <= threshold.

    Returns:
      (deltas, thresholds, ok_flags)
    """
    deltas     = []
    thresholds = []
    ok_flags   = []
    for a, m, v in zip(actual, means, variances):
        delta = abs(a - m)
        thresh = threshold_factor * (v ** 0.5)
        ok = delta <= thresh
        deltas.append(delta)
        thresholds.append(thresh)
        ok_flags.append(ok)
    return deltas, thresholds, ok_flags


def remove_outliers(data: List[float], alpha: float = 0.05) -> List[float]:
    """
    Remove gross errors (outliers) from a sample using the t-test as described in the methodical instructions.
    Returns a new list with outliers removed.
    """
    data = data.copy()
    n = len(data)
    if n < 3:
        return data
    while n > 2:
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        max_dev = max(data, key=lambda x: abs(x - mean))
        t_stat = abs(max_dev - mean) / (std / math.sqrt(n))
        t_crit = t_dist.ppf(1 - alpha/2, n - 2)
        if t_stat > t_crit:
            data.remove(max_dev)
            n -= 1
        else:
            break
    return data


def t_test(sample1: List[float], sample2: List[float], alpha: float = 0.05) -> bool:
    """
    Test the hypothesis that the means of two samples are equal (Student's t-test).
    Returns True if the null hypothesis (means are equal) is NOT rejected.
    """
    n1 = len(sample1)
    n2 = len(sample2)
    if n1 < 2 or n2 < 2:
        return False
    mean1 = statistics.mean(sample1)
    mean2 = statistics.mean(sample2)
    var1 = statistics.variance(sample1)
    var2 = statistics.variance(sample2)
    # Pooled standard deviation
    S_p = math.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    t_value = abs(mean1 - mean2) / (S_p * math.sqrt(1/n1 + 1/n2))
    t_crit = t_dist.ppf(1 - alpha/2, n1 + n2 - 2)
    return t_value < t_crit


def f_test(var1: float, var2: float, n1: int, n2: int, alpha: float = 0.05) -> bool:
    """
    Test the hypothesis that the variances of two samples are equal (Fisher's F-test).
    Returns True if the null hypothesis (variances are equal) is NOT rejected.
    """
    F = max(var1, var2) / min(var1, var2)
    dfn = n1 - 1
    dfd = n2 - 1
    F_crit = f_dist.ppf(1 - alpha/2, dfn, dfd)
    return F < F_crit


def remove_outliers_per_position(runs: list[list[float]], alpha: float = 0.05) -> list[list[float]]:
    """
    Remove outliers for each position (column) in a list of runs.
    Returns a new list of runs with outliers removed per position.
    """
    if not runs:
        return []
    cols = list(zip(*runs))
    cleaned_cols = [remove_outliers(list(col), alpha) for col in cols]
    max_len = max(len(col) for col in cleaned_cols)
    cleaned_runs = []
    for i in range(max_len):
        run = []
        for col in cleaned_cols:
            run.append(col[i] if i < len(col) else None)
        cleaned_runs.append(run)
    cleaned_runs = [run for run in cleaned_runs if all(x is not None for x in run)]
    return cleaned_runs


def calculate_error_rates(results: list[bool]) -> tuple[float, float]:
    """
    Calculate error rates of 1st and 2nd kind based on a list of boolean results.
    P1 = N1 / N0 (legitimate user not identified)
    P2 = N2 / N0 (impostor identified as legitimate)
    Returns (P1, P2)
    """
    N0 = len(results)
    N1 = results.count(False)  # 1-го роду: легітимний не ідентифікований
    N2 = results.count(True)   # 2-го роду: зловмисник ідентифікований як легітимний (якщо є такі дані)
    P1 = N1 / N0 if N0 else 0.0
    P2 = N2 / N0 if N0 else 0.0
    return P1, P2
