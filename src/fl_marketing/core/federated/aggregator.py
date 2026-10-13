from __future__ import annotations

import torch

from fl_marketing.types import ModelUpdate


def fedavg(updates: list[ModelUpdate]) -> dict[str, torch.Tensor]:
    total = sum(u.num_samples for u in updates)
    keys = updates[0].state_dict.keys()
    aggregated: dict[str, torch.Tensor] = {}
    for key in keys:
        weighted = sum(u.state_dict[key].float() * u.num_samples for u in updates)
        aggregated[key] = weighted / total
    return aggregated
