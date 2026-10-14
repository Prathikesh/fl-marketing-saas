from __future__ import annotations

import argparse
from functools import partial
from pathlib import Path

from fl_marketing.config import load_config
from fl_marketing.core.federated.aggregator import coordinate_median, fedavg, trimmed_mean
from fl_marketing.core.federated.attacks import PoisoningClient
from fl_marketing.core.federated.client import FederatedClient
from fl_marketing.core.federated.server import FederatedServer
from fl_marketing.core.training.local_trainer import predict_proba
from fl_marketing.data import store
from fl_marketing.data.loaders import make_loader
from fl_marketing.evaluation.metrics import best_threshold, f1
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

log = get_logger("run_robustness")
PROC = Path("data/processed")

ATTACKER_TID = 0  # the largest tenant turns malicious (worst case under sample weighting)


def build_clients(cfg, tenants, feat_cols, poison: bool):
    fd = len(feat_cols)
    clients = []
    for tid, df in tenants.items():
        loader = make_loader(df[df.split == "train"], feat_cols, 64, True)
        cls = PoisoningClient if (poison and tid == ATTACKER_TID) else FederatedClient
        clients.append(cls(tid, loader, fd, cfg.federated.local_epochs, cfg.federated.local_lr, cfg.federated.mu, None))
    return clients


def score(cfg, tenants, feat_cols, poison, aggregator):
    set_seed(cfg.seed)
    fd = len(feat_cols)
    clients = build_clients(cfg, tenants, feat_cols, poison)
    state = FederatedServer(clients, fd, cfg.federated.rounds, cfg.federated.min_clients, aggregator=aggregator).run()
    model = ConversionNet(in_dim=fd)
    model.load_state_dict(state)
    pooled = store.pooled(tenants)
    vp, vy = predict_proba(model, make_loader(pooled[pooled.split == "val"], feat_cols, 256, False))
    tp, ty = predict_proba(model, make_loader(pooled[pooled.split == "test"], feat_cols, 256, False))
    return f1(ty.numpy(), tp.numpy(), best_threshold(vy.numpy(), vp.numpy()))


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)

    scenarios = [
        ("no attack", False, "FedAvg", fedavg),
        ("1 poisoning tenant", True, "FedAvg", fedavg),
        ("1 poisoning tenant", True, "coordinate median", coordinate_median),
        ("1 poisoning tenant", True, "trimmed mean", partial(trimmed_mean, trim=1)),
    ]
    log.info("robust aggregation vs a model-poisoning tenant (attacker = tenant %d)", ATTACKER_TID)
    log.info("%-22s %-18s %10s", "scenario", "aggregator", "fed F1")
    for label, poison, agg_name, agg in scenarios:
        s = score(cfg, tenants, feat_cols, poison, agg)
        log.info("%-22s %-18s %10.4f", label, agg_name, s)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
