from __future__ import annotations

import argparse
from pathlib import Path

from fl_marketing.baselines.single_tenant import run_single_tenant
from fl_marketing.config import load_config
from fl_marketing.core.training.local_trainer import predict_proba
from fl_marketing.data import store
from fl_marketing.data.loaders import make_loader
from fl_marketing.evaluation.metrics import best_threshold, cross_client_gain, f1
from fl_marketing.models.conversion_net import ConversionNet
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

from run_federated import run as run_federated

log = get_logger("run_evaluation")
PROC = Path("data/processed")


def _per_tenant_federated_f1(model, tenants, feat_cols) -> dict[int, float]:
    out = {}
    for tid, df in tenants.items():
        vl = make_loader(df[df.split == "val"], feat_cols, 256, False)
        tl = make_loader(df[df.split == "test"], feat_cols, 256, False)
        vp, vy = predict_proba(model, vl)
        tp, ty = predict_proba(model, tl)
        out[tid] = f1(ty.numpy(), tp.numpy(), best_threshold(vy.numpy(), vp.numpy()))
    return out


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)
    manifest = store.load_manifest(PROC)
    feat_cols = store.feature_columns(manifest)
    tenants = store.load_all_tenants(PROC, manifest)

    total_epochs = cfg.federated.local_epochs * cfg.federated.rounds
    isolated = run_single_tenant(tenants, feat_cols, total_epochs, cfg.federated.local_lr)

    global_state = run_federated(config_path)
    model = ConversionNet(in_dim=len(feat_cols))
    model.load_state_dict(global_state)
    federated = _per_tenant_federated_f1(model, tenants, feat_cols)

    log.info("cross-client gain: federated vs single-tenant isolated")
    log.info("%-18s %6s %9s %10s %8s", "tenant", "rows", "isolated", "federated", "gain%")
    for t in manifest["tenants"]:
        tid = t["tenant_id"]
        gain = cross_client_gain(federated[tid], isolated[tid]) * 100
        log.info("%-18s %6d %9.4f %10.4f %+8.1f", t["source"], t["rows"], isolated[tid], federated[tid], gain)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
