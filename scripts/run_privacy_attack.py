from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from fl_marketing.config import load_config
from fl_marketing.core.privacy.dp_engine import dp_local_train
from fl_marketing.core.training.local_trainer import local_train
from fl_marketing.data import store
from fl_marketing.data.loaders import make_loader, to_tensors
from fl_marketing.evaluation.privacy_attack import attack_accuracy, build_attack_classifier, _confidence_features
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

log = get_logger("run_privacy_attack")
PROC = Path("data/processed")


def _train_plain(df, feat_cols, epochs, lr):
    model = ConversionNet(in_dim=len(feat_cols))
    local_train(model, make_loader(df, feat_cols, 64, True), epochs, lr, -1)
    return model


def run(config_path: str, n_shadows: int) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    pooled = store.pooled(store.load_all_tenants(PROC, manifest))
    pool = pooled[pooled.split != "test"].reset_index(drop=True)
    epochs = cfg.federated.local_epochs * cfg.federated.rounds
    rng = np.random.default_rng(cfg.seed)

    shadow_examples = []
    for _ in range(n_shadows):
        idx = rng.permutation(len(pool))
        half = len(idx) // 2
        in_df, out_df = pool.iloc[idx[:half]], pool.iloc[idx[half:]]
        shadow = _train_plain(in_df, feat_cols, epochs, cfg.federated.local_lr)
        xin, yin = to_tensors(in_df, feat_cols).tensors
        xout, yout = to_tensors(out_df, feat_cols).tensors
        for f in _confidence_features(shadow, xin, yin):
            shadow_examples.append((f.reshape(1, -1), 1))
        for f in _confidence_features(shadow, xout, yout):
            shadow_examples.append((f.reshape(1, -1), 0))
    attack = build_attack_classifier(shadow_examples)

    idx = rng.permutation(len(pool))
    half = len(idx) // 2
    members, non = pool.iloc[idx[:half]], pool.iloc[idx[half:]]
    m_t = to_tensors(members, feat_cols).tensors
    n_t = to_tensors(non, feat_cols).tensors

    non_private = _train_plain(members, feat_cols, epochs, cfg.federated.local_lr)
    acc_np = attack_accuracy(attack, non_private, m_t, n_t)

    private = ConversionNet(in_dim=len(feat_cols))
    dp_local_train(
        private, make_loader(members, feat_cols, 64, True), epochs, cfg.federated.local_lr, -1,
        cfg.privacy.noise_multiplier, cfg.privacy.max_grad_norm, cfg.privacy.delta,
    )
    acc_dp = attack_accuracy(attack, private, m_t, n_t)

    log.info("membership inference attack (%d shadow models, 50%% baseline)", n_shadows)
    log.info("  non-private target: attack accuracy = %.3f  (advantage %+.1f%%)", acc_np, (acc_np - 0.5) * 100)
    log.info("  DP-private target:  attack accuracy = %.3f  (advantage %+.1f%%, target <= 5%%)", acc_dp, (acc_dp - 0.5) * 100)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--shadows", type=int, default=5)
    args = parser.parse_args()
    run(args.config, args.shadows)


if __name__ == "__main__":
    main()
