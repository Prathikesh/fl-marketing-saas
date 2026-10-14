import random

from fl_marketing.core.federated.strategy import drop_fixed


def test_drop_fixed_removes_exactly_k():
    clients = list(range(5))
    random.seed(0)
    kept = drop_fixed(clients, 2)
    assert len(kept) == 3
    assert set(kept).issubset(set(clients))


def test_drop_fixed_noop_for_zero_or_all():
    clients = list(range(5))
    assert drop_fixed(clients, 0) == clients
    assert drop_fixed(clients, 5) == clients
