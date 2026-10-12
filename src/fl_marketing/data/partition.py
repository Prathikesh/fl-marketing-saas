from __future__ import annotations

import pandas as pd


def partition_by_tenant(df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    raise NotImplementedError


def downsample_tenant(df: pd.DataFrame, fraction: float, seed: int) -> pd.DataFrame:
    raise NotImplementedError
