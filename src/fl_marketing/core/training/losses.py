from __future__ import annotations

import torch
from torch import nn


def binary_loss() -> nn.Module:
    return nn.BCEWithLogitsLoss()
