"""Logic module."""

import math
import statistics
from typing import Any

from scipy.stats import f as f_dist
from scipy.stats import t as t_dist


def compute_session_stats(
    runs: list[list[float]],
) -> tuple[float, float, list[list[float]]]:
    """Compute session statistics.

    Given a list of dwell-time runs (each run is a list of floats for each character),
    compute per-run means, per-run stddev, and also return the raw runs.

    Returns:
        tuple[float, float, list[list[float]]]: the session statistics
    """
    flat = [value for run in runs for value in run]
    if not flat:
        return 0.0, 0.0, runs

    mean_session = statistics.mean(flat)
    stddev = statistics.stdev(flat)

    return mean_session, stddev, runs


def update_aggregate_profile(profile: dict[str, Any], session: dict[str, Any]) -> None:
    """Incrementally update profile['means'] and profile['variances'].

    Args:
        profile: the profile data
        session: the session data

    Profile fields used:
      profile["means"]: List[float]
      profile["variances"]: List[float]  (population variance)
      profile["total_runs"]: int

    Session fields required:
      session["runs"]: List[List[float]]  (accepted dwell runs)
    """
    new_runs = session["runs"]
    num_new = len(new_runs)
    if num_new == 0:
        return

    cols = list(zip(*new_runs, strict=False))
    session_means = [statistics.mean(c) for c in cols]
    session_vars = [statistics.stdev(c) ** 2 for c in cols]

    if profile.get("total_runs", 0) == 0 or not profile.get("means"):
        profile["means"] = session_means
        profile["variances"] = session_vars
        profile["total_runs"] = num_new
        return

    old_means = profile["means"]
    old_vars = profile["variances"]
    old_n = profile["total_runs"]

    updated_means = []
    updated_vars = []

    for _, (m_old, v_old, m_s, v_s) in enumerate(
        zip(old_means, old_vars, session_means, session_vars, strict=False)
    ):
        total_n = old_n + num_new
        m_new = (m_old * old_n + m_s * num_new) / total_n

        delta = m_old - m_s
        pooled = (
            v_old * old_n
            + v_s * num_new
            + (delta * delta) * (old_n * num_new / total_n)
        )
        v_new = pooled / total_n

        updated_means.append(m_new)
        updated_vars.append(v_new)

    profile["means"] = updated_means
    profile["variances"] = updated_vars
    profile["total_runs"] = total_n


def rebuild_profile_from_history(profile: dict[str, Any]) -> None:
    """Completely recompute profile['means'], ['variances'], and ['total_runs'].

    Args:
        profile: the profile data to rebuild
    """
    all_runs = []
    for sess in profile.get("sessions", []):
        all_runs.extend(sess.get("runs", []))
    if not all_runs:
        profile["means"] = []
        profile["variances"] = []
        profile["total_runs"] = 0
        return

    cols = list(zip(*all_runs, strict=False))
    profile["means"] = [statistics.mean(c) for c in cols]
    profile["variances"] = [statistics.stdev(c) ** 2 for c in cols]
    profile["total_runs"] = len(all_runs)


def calculate_authentication_delta(
    actual: list[float],
    means: list[float],
    variances: list[float],
    threshold_factor: float = 2.0,
    min_threshold: float = 5.0,
) -> tuple[list[float], list[float], list[bool]]:
    """Compute the delta, threshold, and ok flag for a single candidate run.

    Args:
        actual: the actual dwell times
        means: the means of the dwell times
        variances: the variances of the dwell times
        threshold_factor: the threshold factor
        min_threshold: the minimum threshold

    Returns:
      (deltas, thresholds, ok_flags)

    Raises:
      ValueError if the input lists have different lengths.
    """
    if not (len(actual) == len(means) == len(variances)):
        raise ValueError(
            f"Input length mismatch: actual={len(actual)}, "
            f"means={len(means)}, variances={len(variances)}"
        )

    deltas: list[float] = []
    thresholds: list[float] = []
    ok_flags: list[bool] = []

    for a, m, v in zip(actual, means, variances, strict=False):
        delta = abs(a - m)
        # compute raw threshold
        raw_th = threshold_factor * (v**0.5)

        # enforce a floor so you never get a zero threshold
        thresh = raw_th if raw_th >= min_threshold else min_threshold
        ok = delta <= thresh

        deltas.append(delta)
        thresholds.append(thresh)
        ok_flags.append(ok)

    return deltas, thresholds, ok_flags


def remove_outliers(data: list[float], alpha: float = 0.05) -> list[float]:
    """Remove gross errors (outliers) from a sample using the t-test.

    Args:
        data: the data to remove outliers from
        alpha: the significance level

    Returns:
        list[float]: the data with outliers removed
    """
    data = data.copy()
    n = len(data)
    if n < 3:
        return data
    while n > 2:
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        if std == 0:
            break
        max_dev = max(data, key=lambda x: abs(x - mean))
        t_stat = abs(max_dev - mean) / (std / math.sqrt(n))
        t_crit = t_dist.ppf(1 - alpha / 2, n - 2)
        if t_stat > t_crit:
            data.remove(max_dev)
            n -= 1
        else:
            break
    return data


def t_test(sample1: list[float], sample2: list[float], alpha: float = 0.05) -> bool:
    """Student's t-test with automatic variance check.

    Args:
        sample1: the first sample
        sample2: the second sample
        alpha: the significance level

    Returns:
        bool: whether the hypothesis of equal means is not rejected
    """
    n1 = len(sample1)
    n2 = len(sample2)
    if n1 < 2 or n2 < 2:
        return False

    mean1 = statistics.mean(sample1)
    mean2 = statistics.mean(sample2)
    var1 = statistics.variance(sample1)
    var2 = statistics.variance(sample2)

    equal_var = f_test(var1, var2, n1, n2, alpha)

    if equal_var:
        s_p = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        t_value = abs(mean1 - mean2) / (s_p * math.sqrt(1 / n1 + 1 / n2))
        df = n1 + n2 - 2
    else:
        t_value = abs(mean1 - mean2) / math.sqrt(var1 / n1 + var2 / n2)
        df_num = (var1 / n1 + var2 / n2) ** 2
        df_den = (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
        df = df_num / df_den if df_den != 0 else 1

    t_crit = t_dist.ppf(1 - alpha / 2, df)
    return t_value < t_crit


def f_test(var1: float, var2: float, n1: int, n2: int, alpha: float = 0.05) -> bool:
    """Fisher's F-test for equality of variances.

    Args:
        var1: the variance of the first sample
        var2: the variance of the second sample
        n1: the size of the first sample
        n2: the size of the second sample
        alpha: the significance level

    Returns:
        bool: whether the hypothesis of equal variances is not rejected
    """
    if var1 == 0 or var2 == 0:
        return True
    if var1 >= var2:
        fisher = var1 / var2 if var2 != 0 else float("inf")
        dfn, dfd = n1 - 1, n2 - 1
    else:
        fisher = var2 / var1 if var1 != 0 else float("inf")
        dfn, dfd = n2 - 1, n1 - 1
    fisher_crit = f_dist.ppf(1 - alpha / 2, dfn, dfd)
    return fisher_crit > fisher


def remove_outliers_per_position(
    runs: list[list[float]], alpha: float = 0.05
) -> list[list[float]]:
    """Remove outlier runs based on per-position t-tests.

    Args:
        runs: the runs to remove outliers from
        alpha: the significance level

    Returns:
        list[list[float]]: the runs with outliers removed
    """
    if not runs:
        return []

    num_positions = len(runs[0])
    outliner_indices: set[int] = set()

    for pos in range(num_positions):
        values_with_idx = [
            (run[pos], idx) for idx, run in enumerate(runs) if len(run) > pos
        ]
        data = values_with_idx
        n = len(data)

        if n < 3:
            continue

        while n > 2:
            mean = statistics.mean(v for v, _ in data)
            std = statistics.stdev(v for v, _ in data)

            if std == 0:
                break

            value, idx = max(data, key=lambda item: abs(item[0] - mean))
            t_stat = abs(value - mean) / (std / math.sqrt(n))
            t_crit = t_dist.ppf(1 - alpha / 2, n - 2)

            if t_stat > t_crit:
                outliner_indices.add(idx)
                data = [item for item in data if item[1] != idx]
                n -= 1
            else:
                break

    return [run for idx, run in enumerate(runs) if idx not in outliner_indices]


def calculate_error_rates(results: list[bool]) -> tuple[float, float]:
    """Calculate error rates of 1st and 2nd kind based on a list of boolean results.

    Args:
        results: the list of boolean results

    Returns:
        tuple[float, float]: the error rates
    """
    n_0 = len(results)

    # 1-го роду: легітимний не ідентифікований  # noqa: RUF003
    n_1 = results.count(False)

    # 2-го роду: зловмисник ідентифікований як легітимний (якщо є такі дані) # noqa: RUF003
    n_2 = results.count(True)

    p_1 = n_1 / n_0 if n_0 else 0.0
    p_2 = n_2 / n_0 if n_0 else 0.0

    return p_1, p_2
