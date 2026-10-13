from __future__ import annotations

import torch
from torch import nn
from torch.utils.data import DataLoader

from fl_marketing.core.training.losses import binary_loss
from fl_marketing.types import ModelUpdate


def local_train(
    model: nn.Module,
    loader: DataLoader,
    epochs: int,
    lr: float,
    tenant_id: int,
    global_params: list[torch.Tensor] | None = None,
    mu: float = 0.0,
) -> ModelUpdate:
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = binary_loss()
    for _ in range(epochs):
        for x, y in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(x), y)
            if global_params is not None and mu > 0:
                prox = sum(((p - gp) ** 2).sum() for p, gp in zip(model.parameters(), global_params))
                loss = loss + (mu / 2) * prox
            loss.backward()
            optimizer.step()
    return ModelUpdate(state_dict=model.state_dict(), num_samples=len(loader.dataset), tenant_id=tenant_id)


@torch.no_grad()
def predict_proba(model: nn.Module, loader: DataLoader) -> tuple[torch.Tensor, torch.Tensor]:
    model.eval()
    probs, targets = [], []
    for x, y in loader:
        probs.append(torch.sigmoid(model(x)))
        targets.append(y)
    return torch.cat(probs).squeeze(1), torch.cat(targets).squeeze(1)
