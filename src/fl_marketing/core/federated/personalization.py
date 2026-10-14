from __future__ import annotations

import torch

from fl_marketing.core.training.losses import binary_loss
from fl_marketing.data.loaders import make_loader
from fl_marketing.models.conversion_net import ConversionNet


def personalize_head(
    global_state: dict[str, torch.Tensor], feat_cols, train_df, epochs: int, lr: float
) -> ConversionNet:
    model = ConversionNet(in_dim=len(feat_cols))
    model.load_state_dict(global_state)

    for p in model.parameters():
        p.requires_grad = False
    head = model.net[-1]
    for p in head.parameters():
        p.requires_grad = True

    loader = make_loader(train_df, feat_cols, batch_size=64, shuffle=True)
    optimizer = torch.optim.Adam(head.parameters(), lr=lr)
    loss_fn = binary_loss()
    model.train()
    for _ in range(epochs):
        for x, y in loader:
            optimizer.zero_grad()
            loss_fn(model(x), y).backward()
            optimizer.step()
    return model
