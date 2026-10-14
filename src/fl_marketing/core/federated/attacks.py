from __future__ import annotations

import torch

from fl_marketing.core.federated.client import FederatedClient
from fl_marketing.types import ModelUpdate


class PoisoningClient(FederatedClient):
    def __init__(self, *args, boost: float = 10.0, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.boost = boost

    def train_round(self, global_state: dict[str, torch.Tensor]) -> ModelUpdate:
        poisoned = {k: -self.boost * v.float() for k, v in global_state.items()}
        return ModelUpdate(state_dict=poisoned, num_samples=len(self.loader.dataset), tenant_id=self.tenant_id)
