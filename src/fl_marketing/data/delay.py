from __future__ import annotations

import numpy as np
import pandas as pd


def inject_label_delay(
    df: pd.DataFrame,
    min_days: int,
    max_days: int,
    launch_span_days: int,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = df.copy()
    n = len(out)
    out["launch_day"] = rng.integers(0, launch_span_days + 1, n)
    delay = rng.integers(min_days, max_days + 1, n)
    out["label_arrival_day"] = out["launch_day"] + delay
    return out
