from __future__ import annotations

import pandas as pd
from torch.utils.data import DataLoader


def make_loader(df: pd.DataFrame, batch_size: int, shuffle: bool = True) -> DataLoader:
    raise NotImplementedError
