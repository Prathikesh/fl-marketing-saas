import numpy as np
import pandas as pd
import torch

from fl_marketing.core.adaptation.adapter import incremental_update
from fl_marketing.core.training.losses import binary_loss
from fl_marketing.data.loaders import make_loader, to_tensors
from fl_marketing.models.conversion_net import ConversionNet


def _batch(n=128):
    rng = np.random.default_rng(0)
    x = rng.random((n, 5)).astype("float32")
    df = pd.DataFrame(x, columns=[f"f{i}" for i in range(5)])
    df["converted"] = (x[:, 0] + x[:, 1] > 1.0).astype(int)
    return df, [f"f{i}" for i in range(5)]


def test_incremental_update_reduces_loss_on_new_batch():
    df, feats = _batch()
    model = ConversionNet(in_dim=len(feats))
    ds = to_tensors(df, feats)
    x, y = ds.tensors
    loss_fn = binary_loss()
    with torch.no_grad():
        before = loss_fn(model(x), y).item()
    incremental_update(model, make_loader(df, feats, batch_size=32), lr=1e-3, epochs=5)
    with torch.no_grad():
        after = loss_fn(model(x), y).item()
    assert after < before
