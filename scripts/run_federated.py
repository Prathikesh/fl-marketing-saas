from __future__ import annotations

import argparse
from pathlib import Path

import torch

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

log = get_logger("run_federated")
PROC = Path("data/processed")


MODELS = Path("models")


def run(config_path: str, private: bool = False, save: bool = False) -> dict[str, torch.Tensor]:
    cfg = load_config(config_path)
    set_seed(cfg.seed)

    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)
    feature_dim = len(feat_cols)
    privacy = cfg.privacy if private else None

    clients = []
    for tid, df in tenants.items():
        train_df = df[df.split == "train"]
        loader = make_loader(train_df, feat_cols, batch_size=64, shuffle=True)
        clients.append(
            FederatedClient(
                tid, loader, feature_dim, cfg.federated.local_epochs, cfg.federated.local_lr, cfg.federated.mu, privacy
            )
        )

    server = FederatedServer(clients, feature_dim, cfg.federated.rounds, cfg.federated.min_clients)
    global_state = server.run()
    audit = server.audit

    model = ConversionNet(in_dim=feature_dim)
    model.load_state_dict(global_state)

    pooled = store.pooled(tenants)
    val_loader = make_loader(pooled[pooled.split == "val"], feat_cols, batch_size=256, shuffle=False)
    vp, vy = predict_proba(model, val_loader)
    thr = best_threshold(vy.numpy(), vp.numpy())

    test_loader = make_loader(pooled[pooled.split == "test"], feat_cols, batch_size=256, shuffle=False)
    tp, ty = predict_proba(model, test_loader)
    global_f1 = f1(ty.numpy(), tp.numpy(), thr)
    log.info("GLOBAL federated F1 on pooled test = %.4f (thr %.2f)", global_f1, thr)
    if private:
        eps = [c.last_epsilon for c in clients if c.last_epsilon is not None]
        if eps:
            log.info("differential privacy: mean per-round epsilon per tenant = %.3f (delta=%.0e)", sum(eps) / len(eps), cfg.privacy.delta)

    for tid, df in tenants.items():
        tl = make_loader(df[df.split == "test"], feat_cols, batch_size=256, shuffle=False)
        p, y = predict_proba(model, tl)
        log.info("  tenant %d (%s): test F1 = %.4f", tid, manifest["tenants"][tid]["source"], f1(y.numpy(), p.numpy(), thr))

    if save:
        MODELS.mkdir(parents=True, exist_ok=True)
        torch.save(
            {"state_dict": global_state, "threshold": float(thr), "feature_dim": feature_dim, "private": private},
            MODELS / "global_model.pt",
        )
        import json

        (MODELS / "audit.json").write_text(json.dumps(audit, indent=2))
        log.info("saved model and audit log to %s", MODELS)

    return global_state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    run(args.config, private=args.private, save=args.save)


if __name__ == "__main__":
    main()
