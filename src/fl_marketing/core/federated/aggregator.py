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


def coordinate_median(updates: list[ModelUpdate]) -> dict[str, torch.Tensor]:
    aggregated: dict[str, torch.Tensor] = {}
    for key in updates[0].state_dict.keys():
        stacked = torch.stack([u.state_dict[key].float() for u in updates])
        aggregated[key] = stacked.median(dim=0).values
    return aggregated


def trimmed_mean(updates: list[ModelUpdate], trim: int = 1) -> dict[str, torch.Tensor]:
    n = len(updates)
    if n <= 2 * trim:
        return coordinate_median(updates)
    aggregated: dict[str, torch.Tensor] = {}
    for key in updates[0].state_dict.keys():
        stacked = torch.stack([u.state_dict[key].float() for u in updates])
        kept = stacked.sort(dim=0).values[trim : n - trim]
        aggregated[key] = kept.mean(dim=0)
    return aggregated
