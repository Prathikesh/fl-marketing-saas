from __future__ import annotations

import pandas as pd

from fl_marketing.core.training.local_trainer import local_train, predict_proba
from fl_marketing.data.loaders import make_loader
from fl_marketing.evaluation.metrics import best_threshold, f1
from fl_marketing.models.conversion_net import ConversionNet


def run_single_tenant(
    tenants: dict[int, pd.DataFrame], feat_cols: list[str], epochs: int, lr: float
) -> dict[int, float]:
    results: dict[int, float] = {}
    for tid, df in tenants.items():
        model = ConversionNet(in_dim=len(feat_cols))
        train_loader = make_loader(df[df.split == "train"], feat_cols, batch_size=64, shuffle=True)
        local_train(model, train_loader, epochs, lr, tid)

        val_loader = make_loader(df[df.split == "val"], feat_cols, batch_size=256, shuffle=False)
        vp, vy = predict_proba(model, val_loader)
        thr = best_threshold(vy.numpy(), vp.numpy())

        test_loader = make_loader(df[df.split == "test"], feat_cols, batch_size=256, shuffle=False)
        tp, ty = predict_proba(model, test_loader)
        results[tid] = f1(ty.numpy(), tp.numpy(), thr)
    return results
