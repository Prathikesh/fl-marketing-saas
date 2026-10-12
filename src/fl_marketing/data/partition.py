from __future__ import annotations

import numpy as np
import pandas as pd


def assign_tenants(df: pd.DataFrame, tenant_key: str, min_rows: int) -> tuple[pd.DataFrame, dict[int, str]]:
    counts = df[tenant_key].value_counts()
    sources = [s for s, c in counts.items() if c >= min_rows]
    mapping = {i: s for i, s in enumerate(sources)}
    reverse = {s: i for i, s in mapping.items()}
    out = df[df[tenant_key].isin(sources)].copy()
    out["tenant_id"] = out[tenant_key].map(reverse)
    return out, mapping


def add_splits(df: pd.DataFrame, val_size: float, test_size: float, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = df.copy()
    out["split"] = "train"
    for _, idx in out.groupby(["tenant_id", "converted"]).groups.items():
        idx = np.array(list(idx))
        rng.shuffle(idx)
        n = len(idx)
        n_test = int(n * test_size)
        n_val = int(n * val_size)
        out.loc[idx[:n_test], "split"] = "test"
        out.loc[idx[n_test:n_test + n_val], "split"] = "val"
    return out


def partition_by_tenant(df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    return {int(t): g.reset_index(drop=True) for t, g in df.groupby("tenant_id")}


def downsample_tenant(df: pd.DataFrame, fraction: float, seed: int) -> pd.DataFrame:
    return df.sample(frac=fraction, random_state=seed).reset_index(drop=True)
