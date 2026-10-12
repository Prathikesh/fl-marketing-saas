from __future__ import annotations


def f1(y_true, y_pred) -> float:
    raise NotImplementedError


def mae(y_true, y_pred) -> float:
    raise NotImplementedError


def cross_client_gain(fed_f1: float, isolated_f1: float) -> float:
    raise NotImplementedError
