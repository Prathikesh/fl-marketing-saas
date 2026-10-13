from __future__ import annotations

import numpy as np
from sklearn.metrics import f1_score


def f1(y_true, y_prob, threshold: float = 0.5) -> float:
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    return float(f1_score(np.asarray(y_true).astype(int), y_pred))


def mae(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def best_threshold(y_true, y_prob, lo: float = 0.2, hi: float = 0.7, step: float = 0.01) -> float:
    thresholds = np.arange(lo, hi, step)
    scores = [f1(y_true, y_prob, float(t)) for t in thresholds]
    return float(thresholds[int(np.argmax(scores))])


def cross_client_gain(fed_f1: float, isolated_f1: float) -> float:
    if isolated_f1 == 0:
        return 0.0
    return (fed_f1 - isolated_f1) / isolated_f1
