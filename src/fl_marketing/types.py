from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class ModelUpdate:
    state_dict: dict[str, torch.Tensor]
    num_samples: int
    tenant_id: int


@dataclass
class BufferEntry:
    campaign_id: str
    tenant_id: int
    prediction: float
    predicted_on_day: int
    expected_label_day: int
    status: str
    actual_label: int | None
