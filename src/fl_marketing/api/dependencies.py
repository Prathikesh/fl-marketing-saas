from __future__ import annotations

import json
from pathlib import Path

import torch

from fl_marketing.core.adaptation.buffer import DelayedLabelBuffer
from fl_marketing.models.conversion_net import ConversionNet

PROC = Path("data/processed")
MODELS = Path("models")


class AppState:
    def __init__(self) -> None:
        manifest = json.loads((PROC / "manifest.json").read_text())
        self.feature_cols = manifest["feature_columns"]
        self.numeric_stats = manifest["numeric_stats"]
        self.tenants = {t["tenant_id"]: t["source"] for t in manifest["tenants"]}

        artifact = torch.load(MODELS / "global_model.pt", weights_only=False)
        self.model = ConversionNet(in_dim=artifact["feature_dim"])
        self.model.load_state_dict(artifact["state_dict"])
        self.model.eval()
        self.threshold = artifact["threshold"]
        self.private = artifact.get("private", False)

        audit_path = MODELS / "audit.json"
        self.audit = json.loads(audit_path.read_text()) if audit_path.exists() else []
        self.buffer = DelayedLabelBuffer()


_state: AppState | None = None


def get_state() -> AppState:
    global _state
    if _state is None:
        _state = AppState()
    return _state
