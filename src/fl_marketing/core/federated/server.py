from __future__ import annotations

import torch

from fl_marketing.core.federated.aggregator import fedavg
from fl_marketing.core.federated.client import FederatedClient
from fl_marketing.core.federated.strategy import drop_fixed, select_clients, tolerate_dropout
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger

log = get_logger("federated")


class FederatedServer:
    def __init__(
        self,
        clients: list[FederatedClient],
        feature_dim: int,
        rounds: int,
        min_clients: int,
        dropout_rate: float = 0.0,
        drop_per_round: int = 0,
    ) -> None:
        self.clients = clients
        self.feature_dim = feature_dim
        self.rounds = rounds
        self.min_clients = min_clients
        self.dropout_rate = dropout_rate
        self.drop_per_round = drop_per_round
        self.audit: list[dict] = []

    def run(self) -> dict[str, torch.Tensor]:
        global_state = ConversionNet(in_dim=self.feature_dim).state_dict()
        for r in range(1, self.rounds + 1):
            if self.drop_per_round > 0:
                participating = drop_fixed(self.clients, self.drop_per_round)
            else:
                participating = select_clients(self.clients, self.dropout_rate)
            updates = [c.train_round(global_state) for c in participating]
            updates = tolerate_dropout(updates, self.min_clients)
            global_state = fedavg(updates)
            self.audit.append({"round": r, "participating_tenants": len(updates)})
            log.info("round %d/%d: aggregated %d tenant updates", r, self.rounds, len(updates))
        return global_state
