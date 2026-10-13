from __future__ import annotations


def current_epsilon(privacy_engine, delta: float) -> float:
    return float(privacy_engine.get_epsilon(delta))
