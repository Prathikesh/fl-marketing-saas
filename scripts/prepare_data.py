from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from fl_marketing.config import load_config
from fl_marketing.data import delay, features, harmonize, ingest, labels, partition
from fl_marketing.utils.logging import get_logger
from fl_marketing.utils.seed import set_seed

log = get_logger("prepare_data")

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")


def run(config_path: str) -> None:
    cfg = load_config(config_path)
    set_seed(cfg.seed)

    df = ingest.load_raw(RAW_DIR / cfg.data.raw_file)
    log.info("loaded raw rows=%d", len(df))

    df = harmonize.harmonize_schema(df)
    df = labels.build_binary_label(df)
    df = features.encode_features(df)
    df = delay.inject_label_delay(
        df,
        min_days=cfg.adaptation.delay_min_days,
        max_days=cfg.adaptation.delay_max_days,
        launch_span_days=cfg.data.launch_span_days,
        seed=cfg.seed,
    )

    df, mapping = partition.assign_tenants(df, tenant_key="lead_source", min_rows=cfg.data.min_tenant_rows)
    df = partition.add_splits(df, val_size=cfg.data.val_size, test_size=cfg.data.test_size, seed=cfg.seed)

    feat_cols = features.feature_columns(df.drop(columns=["tenant_id", "launch_day", "label_arrival_day", "split"]))
    tenants = partition.partition_by_tenant(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed": cfg.seed,
        "raw_file": cfg.data.raw_file,
        "feature_count": len(feat_cols),
        "feature_columns": feat_cols,
        "tenants": [],
    }
    keep = feat_cols + ["converted", "launch_day", "label_arrival_day", "split"]
    for tid, g in tenants.items():
        out_path = OUT_DIR / f"tenant_{tid}.csv"
        g[keep].to_csv(out_path, index=False)
        manifest["tenants"].append(
            {
                "tenant_id": tid,
                "source": mapping[tid],
                "rows": int(len(g)),
                "conversion_rate": round(float(g["converted"].mean()), 4),
            }
        )
        log.info("tenant %d (%s): rows=%d conv=%.3f", tid, mapping[tid], len(g), g["converted"].mean())

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    log.info("wrote %d tenants + manifest to %s", len(tenants), OUT_DIR)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/default.yaml")
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
