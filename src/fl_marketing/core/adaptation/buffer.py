from __future__ import annotations

from fl_marketing.types import BufferEntry


class DelayedLabelBuffer:
    def register(self, campaign_id: str, tenant_id: int, prediction: float, day: int, expected_day: int) -> None:
        raise NotImplementedError

    def fulfill(self, campaign_id: str, actual_label: int) -> BufferEntry:
        raise NotImplementedError

    def fulfilled_count(self, tenant_id: int) -> int:
        raise NotImplementedError
