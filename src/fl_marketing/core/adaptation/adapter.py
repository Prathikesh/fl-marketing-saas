from __future__ import annotations

from torch import nn


def incremental_update(model: nn.Module, new_batch, lr: float):
    raise NotImplementedError
