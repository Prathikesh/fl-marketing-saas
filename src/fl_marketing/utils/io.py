from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_csv(path: str | Path) -> pd.DataFrame:
    raise NotImplementedError


def write_parquet(df: pd.DataFrame, path: str | Path) -> None:
    raise NotImplementedError
