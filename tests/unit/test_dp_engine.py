import pandas as pd

from fl_marketing.core.privacy.dp_engine import dp_local_train
from fl_marketing.data.loaders import make_loader
from fl_marketing.models.conversion_net import ConversionNet


def _tiny_df(n=256):
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.random((n, 6)).astype("float32")
    df = pd.DataFrame(x, columns=[f"f{i}" for i in range(6)])
    df["converted"] = (x[:, 0] > 0.5).astype(int)
    return df, [f"f{i}" for i in range(6)]


def test_dp_local_train_returns_update_and_positive_epsilon():
    df, feats = _tiny_df()
    model = ConversionNet(in_dim=len(feats))
    loader = make_loader(df, feats, batch_size=32)
    update, epsilon = dp_local_train(
        model, loader, epochs=1, lr=1e-3, tenant_id=0, noise_multiplier=1.0, max_grad_norm=1.0, delta=1e-5
    )
    assert update.num_samples == len(df)
    assert epsilon > 0
    assert set(update.state_dict.keys()) == set(ConversionNet(in_dim=len(feats)).state_dict().keys())
