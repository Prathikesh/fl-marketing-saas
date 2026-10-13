from __future__ import annotations

import torch
from torch import nn
from torch.utils.data import DataLoader

from fl_marketing.core.training.losses import binary_loss
from fl_marketing.types import ModelUpdate


def dp_local_train(
    model: nn.Module,
    loader: DataLoader,
    epochs: int,
    lr: float,
    tenant_id: int,
    noise_multiplier: float,
    max_grad_norm: float,
    delta: float,
) -> tuple[ModelUpdate, float]:
    from opacus import PrivacyEngine

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = binary_loss()
    engine = PrivacyEngine()
    dp_model, dp_optimizer, dp_loader = engine.make_private(
        module=model,
        optimizer=optimizer,
        data_loader=loader,
        noise_multiplier=noise_multiplier,
        max_grad_norm=max_grad_norm,
    )
    dp_model.train()
    for _ in range(epochs):
        for x, y in dp_loader:
            dp_optimizer.zero_grad()
            loss_fn(dp_model(x), y).backward()
            dp_optimizer.step()

    epsilon = engine.get_epsilon(delta)
    state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    return ModelUpdate(state_dict=state, num_samples=len(loader.dataset), tenant_id=tenant_id), epsilon
