from __future__ import annotations

import torch
from torch import nn
from torch.utils.data import DataLoader

from fl_marketing.core.training.losses import binary_loss


def incremental_update(model: nn.Module, loader: DataLoader, lr: float, epochs: int = 1) -> nn.Module:
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = binary_loss()
    for _ in range(epochs):
        for x, y in loader:
            optimizer.zero_grad()
            loss_fn(model(x), y).backward()
            optimizer.step()
    return model
