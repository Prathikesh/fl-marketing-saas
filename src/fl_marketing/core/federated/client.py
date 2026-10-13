from __future__ import annotations

import torch
from torch.utils.data import DataLoader

from fl_marketing.config import PrivacyConfig
from fl_marketing.core.privacy.dp_engine import dp_local_train
from fl_marketing.core.training.local_trainer import local_train
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.types import ModelUpdate


class FederatedClient:
    def __init__(
        self,
        tenant_id: int,
        loader: DataLoader,
        feature_dim: int,
        epochs: int,
        lr: float,
        mu: float = 0.0,
        privacy: PrivacyConfig | None = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.loader = loader
        self.feature_dim = feature_dim
        self.epochs = epochs
        self.lr = lr
        self.mu = mu
        self.privacy = privacy
        self.last_epsilon: float | None = None

    def train_round(self, global_state: dict[str, torch.Tensor]) -> ModelUpdate:
        model = ConversionNet(in_dim=self.feature_dim)
        model.load_state_dict(global_state)
        if self.privacy is not None:
            update, epsilon = dp_local_train(
                model,
                self.loader,
                self.epochs,
                self.lr,
                self.tenant_id,
                self.privacy.noise_multiplier,
                self.privacy.max_grad_norm,
                self.privacy.delta,
            )
            self.last_epsilon = epsilon
            return update
        global_params = [p.detach().clone() for p in model.parameters()] if self.mu > 0 else None
        return local_train(model, self.loader, self.epochs, self.lr, self.tenant_id, global_params, self.mu)
