from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from fl_marketing.config import load_config
from fl_marketing.data.loaders import make_loader
from fl_marketing.core.training.local_trainer import local_train, predict_proba
from fl_marketing.evaluation.metrics import f1
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

log = get_logger("sanity_check")
PROC = Path("data/processed")


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)

    manifest = json.loads((PROC / "manifest.json").read_text())
    feat_cols = manifest["feature_columns"]

    frames = [pd.read_csv(PROC / f"tenant_{t['tenant_id']}.csv") for t in manifest["tenants"]]
    pooled = pd.concat(frames, ignore_index=True)
    train_df = pooled[pooled.split == "train"]
    test_df = pooled[pooled.split == "test"]

    model = ConversionNet(in_dim=len(feat_cols))
    train_loader = make_loader(train_df, feat_cols, batch_size=64, shuffle=True)
    test_loader = make_loader(test_df, feat_cols, batch_size=256, shuffle=False)

    local_train(model, train_loader, epochs=60, lr=1e-3, tenant_id=-1)
    probs, targets = predict_proba(model, test_loader)
    score = f1(targets.numpy(), probs.numpy())

    log.info("centralized pooled F1 on test = %.4f (target >= 0.82)", score)
    log.info("train rows=%d test rows=%d features=%d", len(train_df), len(test_df), len(feat_cols))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
