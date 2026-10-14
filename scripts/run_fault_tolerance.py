from __future__ import annotations

import argparse
from pathlib import Path

from fl_marketing.config import load_config
from fl_marketing.core.federated.client import FederatedClient
from fl_marketing.core.federated.server import FederatedServer
from fl_marketing.core.training.local_trainer import predict_proba
from fl_marketing.data import store
from fl_marketing.data.loaders import make_loader
from fl_marketing.evaluation.metrics import best_threshold, f1
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

log = get_logger("run_fault_tolerance")
PROC = Path("data/processed")

DROP_COUNTS = [0, 1, 2, 3]


def train_with_dropout(cfg, tenants, feat_cols, k):
    fd = len(feat_cols)
    clients = [
        FederatedClient(tid, make_loader(df[df.split == "train"], feat_cols, 64, True), fd,
                        cfg.federated.local_epochs, cfg.federated.local_lr, cfg.federated.mu, None)
        for tid, df in tenants.items()
    ]
    server = FederatedServer(clients, fd, cfg.federated.rounds, cfg.federated.min_clients, drop_per_round=k)
    state = server.run()
    model = ConversionNet(in_dim=fd)
    model.load_state_dict(state)
    pooled = store.pooled(tenants)
    vp, vy = predict_proba(model, make_loader(pooled[pooled.split == "val"], feat_cols, 256, False))
    tp, ty = predict_proba(model, make_loader(pooled[pooled.split == "test"], feat_cols, 256, False))
    score = f1(ty.numpy(), tp.numpy(), best_threshold(vy.numpy(), vp.numpy()))
    avg_part = sum(a["participating_tenants"] for a in server.audit) / len(server.audit)
    return score, avg_part


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)
    n = len(tenants)

    log.info("fault tolerance: fixed per-round tenant dropout (%d tenants, min_clients=%d)", n, cfg.federated.min_clients)
    log.info("%-14s %12s %18s %10s", "dropped/round", "% offline", "avg tenants/round", "fed F1")
    for k in DROP_COUNTS:
        set_seed(cfg.seed)
        pct = 100 * k / n
        try:
            score, avg_part = train_with_dropout(cfg, tenants, feat_cols, k)
            log.info("%-14d %11.0f%% %18.1f %10.4f", k, pct, avg_part, score)
        except RuntimeError:
            log.info("%-14d %11.0f%% %18s %10s", k, pct, "<quorum", "aborted (min_clients enforced)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
