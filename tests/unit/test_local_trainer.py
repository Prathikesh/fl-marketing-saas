import torch

from fl_marketing.core.training.local_trainer import local_train, predict_proba
from fl_marketing.data.loaders import make_loader
from fl_marketing.models.conversion_net import ConversionNet
import pandas as pd


def _tiny_df(n=64):
    rng = torch.Generator().manual_seed(0)
    x = torch.rand(n, 4, generator=rng)
    y = (x[:, 0] > 0.5).int()
    df = pd.DataFrame(x.numpy(), columns=[f"f{i}" for i in range(4)])
    df["converted"] = y.numpy()
    return df, [f"f{i}" for i in range(4)]


def test_local_train_returns_update_with_sample_count():
    df, feats = _tiny_df()
    model = ConversionNet(in_dim=len(feats))
    loader = make_loader(df, feats, batch_size=16)
    update = local_train(model, loader, epochs=1, lr=1e-3, tenant_id=2)
    assert update.tenant_id == 2
    assert update.num_samples == len(df)
    assert set(update.state_dict.keys()) == set(model.state_dict().keys())


def test_predict_proba_shapes_and_range():
    df, feats = _tiny_df()
    model = ConversionNet(in_dim=len(feats))
    loader = make_loader(df, feats, batch_size=16, shuffle=False)
    probs, targets = predict_proba(model, loader)
    assert probs.shape == targets.shape == (len(df),)
    assert float(probs.min()) >= 0.0 and float(probs.max()) <= 1.0
