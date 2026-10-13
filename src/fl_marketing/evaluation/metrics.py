from __future__ import annotations

import numpy as np
from sklearn.metrics import f1_score


def f1(y_true, y_prob, threshold: float = 0.5) -> float:
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    return float(f1_score(np.asarray(y_true).astype(int), y_pred))


def mae(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def cross_client_gain(fed_f1: float, isolated_f1: float) -> float:
    if isolated_f1 == 0:
        return 0.0
    return (fed_f1 - isolated_f1) / isolated_f1
