from __future__ import annotations

import argparse
from pathlib import Path

from fl_marketing.baselines.single_tenant import run_single_tenant
from fl_marketing.config import load_config
from fl_marketing.core.federated.personalization import personalize_head
from fl_marketing.core.training.local_trainer import predict_proba
from fl_marketing.data import store
from fl_marketing.data.loaders import make_loader
from fl_marketing.evaluation.metrics import best_threshold, cross_client_gain, f1
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

from run_federated import run as run_federated

log = get_logger("run_personalization")
PROC = Path("data/processed")

HEAD_EPOCHS = 8
HEAD_LR = 0.001


def _tenant_f1(model, df, feat_cols) -> float:
    vp, vy = predict_proba(model, make_loader(df[df.split == "val"], feat_cols, 256, False))
    tp, ty = predict_proba(model, make_loader(df[df.split == "test"], feat_cols, 256, False))
    return f1(ty.numpy(), tp.numpy(), best_threshold(vy.numpy(), vp.numpy()))


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)

    total_epochs = cfg.federated.local_epochs * cfg.federated.rounds
    isolated = run_single_tenant(tenants, feat_cols, total_epochs, cfg.federated.local_lr)

    global_state = run_federated(config_path)
    shared = ConversionNet(in_dim=len(feat_cols))
    shared.load_state_dict(global_state)

    log.info("personalization: shared federated backbone + per-tenant fine-tuned head")
    log.info("%-18s %6s %9s %9s %13s %10s", "tenant", "rows", "isolated", "shared", "personalized", "gain%")
    for t in manifest["tenants"]:
        tid = t["tenant_id"]
        df = tenants[tid]
        shared_f1 = _tenant_f1(shared, df, feat_cols)
        pmodel = personalize_head(global_state, feat_cols, df[df.split == "train"], HEAD_EPOCHS, HEAD_LR)
        pers_f1 = _tenant_f1(pmodel, df, feat_cols)
        gain = cross_client_gain(pers_f1, isolated[tid]) * 100
        log.info("%-18s %6d %9.4f %9.4f %13.4f %+10.1f", t["source"], t["rows"], isolated[tid], shared_f1, pers_f1, gain)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
