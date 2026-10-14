from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from fl_marketing.config import load_config
from fl_marketing.core.federated.client import FederatedClient
from fl_marketing.core.federated.server import FederatedServer
from fl_marketing.core.privacy.dp_engine import dp_local_train
from fl_marketing.core.training.local_trainer import local_train, predict_proba
from fl_marketing.data import store
from fl_marketing.data.loaders import make_loader, to_tensors
from fl_marketing.evaluation.metrics import best_threshold, f1
from fl_marketing.evaluation.privacy_attack import attack_accuracy, build_attack_classifier, _confidence_features
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

log = get_logger("run_epsilon_sweep")
PROC = Path("data/processed")

# (label, noise_multiplier) — higher noise = stronger privacy (smaller epsilon)
SETTINGS = [("non-private", None), ("strong (~0.5)", 1.6), ("medium (~1.0)", 1.1), ("weak (~2.0)", 0.8)]


def federated_score(cfg, tenants, feat_cols, noise):
    fd = len(feat_cols)
    privacy = cfg.privacy.model_copy(update={"noise_multiplier": noise}) if noise is not None else None
    clients = [
        FederatedClient(tid, make_loader(df[df.split == "train"], feat_cols, 64, True), fd,
                        cfg.federated.local_epochs, cfg.federated.local_lr, cfg.federated.mu, privacy)
        for tid, df in tenants.items()
    ]
    state = FederatedServer(clients, fd, cfg.federated.rounds, cfg.federated.min_clients).run()
    model = ConversionNet(in_dim=fd)
    model.load_state_dict(state)
    pooled = store.pooled(tenants)
    vp, vy = predict_proba(model, make_loader(pooled[pooled.split == "val"], feat_cols, 256, False))
    tp, ty = predict_proba(model, make_loader(pooled[pooled.split == "test"], feat_cols, 256, False))
    score = f1(ty.numpy(), tp.numpy(), best_threshold(vy.numpy(), vp.numpy()))
    eps = [c.last_epsilon for c in clients if c.last_epsilon is not None]
    return score, (sum(eps) / len(eps) if eps else None)


def leakage(cfg, attack, members_t, non_t, feat_cols, members, epochs, noise):
    model = ConversionNet(in_dim=len(feat_cols))
    loader = make_loader(members, feat_cols, 64, True)
    if noise is None:
        local_train(model, loader, epochs, cfg.federated.local_lr, -1)
    else:
        dp_local_train(model, loader, epochs, cfg.federated.local_lr, -1,
                       noise, cfg.privacy.max_grad_norm, cfg.privacy.delta)
    return (attack_accuracy(attack, model, members_t, non_t) - 0.5) * 100


def run(config_path: str, n_shadows: int) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)
    pooled = store.pooled(tenants)
    pool = pooled[pooled.split != "test"].reset_index(drop=True)
    epochs = cfg.federated.local_epochs * cfg.federated.rounds
    rng = np.random.default_rng(cfg.seed)

    shadow_examples = []
    for _ in range(n_shadows):
        idx = rng.permutation(len(pool))
        half = len(idx) // 2
        in_df, out_df = pool.iloc[idx[:half]], pool.iloc[idx[half:]]
        shadow = ConversionNet(in_dim=len(feat_cols))
        local_train(shadow, make_loader(in_df, feat_cols, 64, True), epochs, cfg.federated.local_lr, -1)
        xin, yin = to_tensors(in_df, feat_cols).tensors
        xout, yout = to_tensors(out_df, feat_cols).tensors
        for fv in _confidence_features(shadow, xin, yin):
            shadow_examples.append((fv.reshape(1, -1), 1))
        for fv in _confidence_features(shadow, xout, yout):
            shadow_examples.append((fv.reshape(1, -1), 0))
    attack = build_attack_classifier(shadow_examples)

    idx = rng.permutation(len(pool))
    half = len(idx) // 2
    members, non = pool.iloc[idx[:half]], pool.iloc[idx[half:]]
    members_t, non_t = to_tensors(members, feat_cols).tensors, to_tensors(non, feat_cols).tensors

    log.info("epsilon sweep: privacy vs accuracy vs leakage (%d shadow models)", n_shadows)
    log.info("%-16s %10s %12s %10s %14s", "setting", "noise", "eps/round", "fed F1", "mi advantage%")
    for label, noise in SETTINGS:
        set_seed(cfg.seed)
        score, eps = federated_score(cfg, tenants, feat_cols, noise)
        adv = leakage(cfg, attack, members_t, non_t, feat_cols, members, epochs, noise)
        noise_s = "-" if noise is None else f"{noise:.1f}"
        eps_s = "inf" if eps is None else f"{eps:.2f}"
        log.info("%-16s %10s %12s %10.4f %+14.1f", label, noise_s, eps_s, score, adv)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--shadows", type=int, default=5)
    args = parser.parse_args()
    run(args.config, args.shadows)


if __name__ == "__main__":
    main()
