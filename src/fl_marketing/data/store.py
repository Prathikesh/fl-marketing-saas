from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PASSTHROUGH = ["campaign_id", "converted", "launch_day", "label_arrival_day", "split"]


def load_manifest(proc_dir: str | Path) -> dict:
    return json.loads((Path(proc_dir) / "manifest.json").read_text())


def feature_columns(manifest: dict) -> list[str]:
    return manifest["feature_columns"]


def load_tenant(proc_dir: str | Path, tenant_id: int) -> pd.DataFrame:
    return pd.read_csv(Path(proc_dir) / f"tenant_{tenant_id}.csv")


def load_all_tenants(proc_dir: str | Path, manifest: dict) -> dict[int, pd.DataFrame]:
    return {t["tenant_id"]: load_tenant(proc_dir, t["tenant_id"]) for t in manifest["tenants"]}


def pooled(tenants: dict[int, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(tenants.values(), ignore_index=True)
