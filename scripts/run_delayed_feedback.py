from __future__ import annotations

import argparse
import copy
from pathlib import Path

import numpy as np

from fl_marketing.config import load_config
from fl_marketing.core.adaptation.adapter import incremental_update
from fl_marketing.core.training.local_trainer import predict_proba
from fl_marketing.data import store
from fl_marketing.data.loaders import make_loader
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

from run_federated import run as run_federated

log = get_logger("run_delayed_feedback")
PROC = Path("data/processed")


def _drift_window(pool, size: int, flip_fraction: float, rng) -> "object":
    window = pool.sample(n=size, replace=True, random_state=int(rng.integers(1e9))).reset_index(drop=True)
    n_flip = int(round(flip_fraction * size))
    if n_flip > 0:
        flip_idx = rng.choice(size, size=n_flip, replace=False)
        window.loc[flip_idx, "converted"] = 1 - window.loc[flip_idx, "converted"]
    return window


def _rate_error(model, window_df, feat_cols) -> float:
    probs, targets = predict_proba(model, make_loader(window_df, feat_cols, 256, shuffle=False))
    return abs(float(probs.mean()) - float(targets.mean()))


def run(config_path: str, windows: int, delay: int, window_size: int, max_flip: float) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)
    pooled = store.pooled(tenants)
    test = pooled[pooled.split == "test"]

    global_state = run_federated(config_path)
    static_model = ConversionNet(in_dim=len(feat_cols))
    static_model.load_state_dict(global_state)
    adaptive_model = copy.deepcopy(static_model)

    rng = np.random.default_rng(cfg.seed)
    flips = np.linspace(0.0, max_flip, windows)
    window_data = [_drift_window(test, window_size, float(f), rng) for f in flips]

    static_errs, adaptive_errs = [], []
    for t in range(windows):
        arrived = t - delay
        if arrived >= 0:
            incremental_update(
                adaptive_model,
                make_loader(window_data[arrived], feat_cols, 64, shuffle=True),
                cfg.adaptation.adapt_lr,
                cfg.adaptation.adapt_epochs,
            )
        static_errs.append(_rate_error(static_model, window_data[t], feat_cols))
        adaptive_errs.append(_rate_error(adaptive_model, window_data[t], feat_cols))

    mae_static = float(np.mean(static_errs))
    mae_adaptive = float(np.mean(adaptive_errs))
    reduction = (mae_static - mae_adaptive) / mae_static * 100 if mae_static > 0 else 0.0

    log.info("delayed-feedback MAE over %d windows (concept drift up to %.0f%% label flips, label delay %d windows)", windows, max_flip * 100, delay)
    log.info("  no-delay baseline (static) MAE  = %.4f", mae_static)
    log.info("  proposed (buffer + adaptation)  = %.4f", mae_adaptive)
    log.info("  MAE reduction = %.1f%% (target >= 20%%)", reduction)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--windows", type=int, default=10)
    parser.add_argument("--delay", type=int, default=2)
    parser.add_argument("--window-size", type=int, default=300)
    parser.add_argument("--max-flip", type=float, default=0.45)
    args = parser.parse_args()
    run(args.config, args.windows, args.delay, args.window_size, args.max_flip)


if __name__ == "__main__":
    main()
