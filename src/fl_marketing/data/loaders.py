from __future__ import annotations

import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset


def to_tensors(df: pd.DataFrame, feature_cols: list[str]) -> TensorDataset:
    x = torch.tensor(df[feature_cols].to_numpy(dtype="float32"))
    y = torch.tensor(df["converted"].to_numpy(dtype="float32")).unsqueeze(1)
    return TensorDataset(x, y)


def make_loader(df: pd.DataFrame, feature_cols: list[str], batch_size: int, shuffle: bool = True) -> DataLoader:
    return DataLoader(to_tensors(df, feature_cols), batch_size=batch_size, shuffle=shuffle)
