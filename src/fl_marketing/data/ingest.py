from __future__ import annotations

from pathlib import Path

import pandas as pd

MISSING_TOKENS = ["Select", "select", ""]


def load_raw(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.replace(MISSING_TOKENS, pd.NA)
    return df
