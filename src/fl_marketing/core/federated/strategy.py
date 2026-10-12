from __future__ import annotations

from fl_marketing.types import ModelUpdate


def select_clients(clients: list, min_clients: int) -> list:
    raise NotImplementedError


def tolerate_dropout(updates: list[ModelUpdate], min_clients: int) -> list[ModelUpdate]:
    raise NotImplementedError
