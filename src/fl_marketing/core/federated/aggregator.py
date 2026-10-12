from __future__ import annotations

import torch

from fl_marketing.types import ModelUpdate


def fedavg(updates: list[ModelUpdate]) -> dict[str, torch.Tensor]:
    raise NotImplementedError
