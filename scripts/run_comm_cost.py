from __future__ import annotations

import argparse
from pathlib import Path

from fl_marketing.config import load_config
from fl_marketing.data import store
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger

log = get_logger("run_comm_cost")
PROC = Path("data/processed")
BYTES_PER_FLOAT = 4


def model_update_bytes(feature_dim: int) -> int:
    model = ConversionNet(in_dim=feature_dim)
    return sum(p.numel() for p in model.parameters()) * BYTES_PER_FLOAT


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)
    fd = len(feat_cols)
    n_tenants = len(tenants)
    rounds = cfg.federated.rounds

    update = model_update_bytes(fd)
    # Federated: each round every tenant downloads the global model and uploads its update.
    per_round = n_tenants * update * 2
    fed_total = per_round * rounds

    # Centralized: every tenant ships its raw training rows to the server once.
    train_rows = sum(int((df.split == "train").sum()) for df in tenants.values())
    centralized_total = train_rows * fd * BYTES_PER_FLOAT

    log.info("communication cost: federated vs centralized (%d tenants, %d rounds, %d features)", n_tenants, rounds, fd)
    log.info("  model update size (one direction)      = %s (%d params)", human(update), update // BYTES_PER_FLOAT)
    log.info("  federated traffic per round (all up+down) = %s", human(per_round))
    log.info("  federated traffic over all rounds      = %s", human(fed_total))
    log.info("  centralized one-time raw-data upload   = %s (%d training rows)", human(centralized_total), train_rows)
    ratio = fed_total / centralized_total if centralized_total else 0
    log.info("  federated / centralized ratio          = %.2fx", ratio)
    breakeven = centralized_total / per_round if per_round else 0
    log.info("  break-even                             = %.1f rounds; raw data never leaves a tenant regardless", breakeven)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
