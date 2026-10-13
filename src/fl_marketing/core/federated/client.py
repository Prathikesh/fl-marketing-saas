from __future__ import annotations

import torch
from torch.utils.data import DataLoader

from fl_marketing.core.training.local_trainer import local_train
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.types import ModelUpdate


class FederatedClient:
    def __init__(
        self, tenant_id: int, loader: DataLoader, feature_dim: int, epochs: int, lr: float, mu: float = 0.0
    ) -> None:
        self.tenant_id = tenant_id
        self.loader = loader
        self.feature_dim = feature_dim
        self.epochs = epochs
        self.lr = lr
        self.mu = mu

    def train_round(self, global_state: dict[str, torch.Tensor]) -> ModelUpdate:
        model = ConversionNet(in_dim=self.feature_dim)
        model.load_state_dict(global_state)
        global_params = [p.detach().clone() for p in model.parameters()] if self.mu > 0 else None
        return local_train(model, self.loader, self.epochs, self.lr, self.tenant_id, global_params, self.mu)
