from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class DataConfig(BaseModel):
    raw_file: str
    tenant_key: str
    min_tenant_rows: int
    launch_span_days: int
    val_size: float
    test_size: float


class PrivacyConfig(BaseModel):
    epsilon: float
    noise_multiplier: float
    max_grad_norm: float
    delta: float


class FederatedConfig(BaseModel):
    num_tenants: int
    rounds: int
    local_epochs: int
    local_lr: float
    mu: float
    min_clients: int


class AdaptationConfig(BaseModel):
    buffer_threshold: int
    delay_min_days: int
    delay_max_days: int
    adapt_lr: float


class Config(BaseModel):
    seed: int
    data: DataConfig
    privacy: PrivacyConfig
    federated: FederatedConfig
    adaptation: AdaptationConfig


def load_config(path: str | Path) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(**data)
