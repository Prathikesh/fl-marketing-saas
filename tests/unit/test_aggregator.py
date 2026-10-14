import torch

from fl_marketing.core.federated.aggregator import coordinate_median, fedavg, trimmed_mean
from fl_marketing.core.federated.strategy import tolerate_dropout
from fl_marketing.types import ModelUpdate


def _u(value):
    return ModelUpdate(state_dict={"w": torch.tensor([value])}, num_samples=1, tenant_id=0)


def test_fedavg_is_sample_weighted():
    a = ModelUpdate(state_dict={"w": torch.tensor([0.0])}, num_samples=1, tenant_id=0)
    b = ModelUpdate(state_dict={"w": torch.tensor([10.0])}, num_samples=3, tenant_id=1)
    out = fedavg([a, b])
    assert torch.allclose(out["w"], torch.tensor([7.5]))


def test_coordinate_median_ignores_outlier():
    out = coordinate_median([_u(0.0), _u(10.0), _u(1000.0)])
    assert torch.allclose(out["w"], torch.tensor([10.0]))


def test_trimmed_mean_drops_extremes():
    out = trimmed_mean([_u(0.0), _u(10.0), _u(1000.0)], trim=1)
    assert torch.allclose(out["w"], torch.tensor([10.0]))


def test_tolerate_dropout_raises_below_minimum():
    updates = [ModelUpdate(state_dict={"w": torch.tensor([1.0])}, num_samples=1, tenant_id=0)]
    try:
        tolerate_dropout(updates, min_clients=3)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass
