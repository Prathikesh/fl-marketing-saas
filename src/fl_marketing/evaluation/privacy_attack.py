from __future__ import annotations

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from torch import nn


def _confidence_features(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        p = torch.sigmoid(model(x)).numpy().ravel()
    target = y.numpy().ravel()
    p_true = np.where(target == 1, p, 1 - p)
    loss = -np.log(np.clip(p_true, 1e-7, 1.0))
    return np.column_stack([p_true, loss])


def build_attack_classifier(shadow_examples: list[tuple[np.ndarray, int]]) -> LogisticRegression:
    x = np.vstack([f for f, _ in shadow_examples])
    y = np.array([m for _, m in shadow_examples])
    return LogisticRegression(max_iter=1000).fit(x, y)


def attack_accuracy(
    attack_clf: LogisticRegression,
    target_model: nn.Module,
    members: tuple[torch.Tensor, torch.Tensor],
    non_members: tuple[torch.Tensor, torch.Tensor],
) -> float:
    f_in = _confidence_features(target_model, *members)
    f_out = _confidence_features(target_model, *non_members)
    x = np.vstack([f_in, f_out])
    y = np.r_[np.ones(len(f_in)), np.zeros(len(f_out))]
    return float((attack_clf.predict(x) == y).mean())
