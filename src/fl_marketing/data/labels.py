from __future__ import annotations

import pandas as pd


def build_binary_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["converted"] = out["converted"].astype(int)
    return out
