from __future__ import annotations

from torch import nn

from fl_marketing.types import ModelUpdate


def local_train(model: nn.Module, loader, epochs: int, lr: float, tenant_id: int) -> ModelUpdate:
    raise NotImplementedError
