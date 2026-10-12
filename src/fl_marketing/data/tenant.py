from __future__ import annotations

import pandas as pd


class Tenant:
    def __init__(self, tenant_id: int, data: pd.DataFrame) -> None:
        self.tenant_id = tenant_id
        self._data = data

    def batches(self, batch_size: int):
        raise NotImplementedError
