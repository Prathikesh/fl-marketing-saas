from __future__ import annotations

import random

from fl_marketing.core.federated.client import FederatedClient
from fl_marketing.types import ModelUpdate


def select_clients(clients: list[FederatedClient], dropout_rate: float = 0.0) -> list[FederatedClient]:
    if dropout_rate <= 0:
        return clients
    kept = [c for c in clients if random.random() >= dropout_rate]
    return kept or clients


def drop_fixed(clients: list[FederatedClient], k: int) -> list[FederatedClient]:
    if k <= 0 or k >= len(clients):
        return clients
    offline = set(random.sample(range(len(clients)), k))
    return [c for i, c in enumerate(clients) if i not in offline]


def tolerate_dropout(updates: list[ModelUpdate], min_clients: int) -> list[ModelUpdate]:
    if len(updates) < min_clients:
        raise RuntimeError(f"only {len(updates)} updates received, need at least {min_clients}")
    return updates
