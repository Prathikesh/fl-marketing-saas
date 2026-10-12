from __future__ import annotations

from fl_marketing.types import ModelUpdate


class FederatedClient:
    def __init__(self, tenant) -> None:
        self.tenant = tenant

    def train_round(self, global_state) -> ModelUpdate:
        raise NotImplementedError
