from __future__ import annotations

from torch import nn


def make_private(model: nn.Module, optimizer, loader, noise_multiplier: float, max_grad_norm: float):
    raise NotImplementedError
