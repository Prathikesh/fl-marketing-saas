from __future__ import annotations

from fl_marketing.types import BufferEntry


class DelayedLabelBuffer:
    def __init__(self) -> None:
        self._entries: dict[str, BufferEntry] = {}

    def register(self, campaign_id: str, tenant_id: int, prediction: float, day: int, expected_day: int) -> None:
        self._entries[campaign_id] = BufferEntry(
            campaign_id=campaign_id,
            tenant_id=tenant_id,
            prediction=prediction,
            predicted_on_day=day,
            expected_label_day=expected_day,
            status="pending",
            actual_label=None,
        )

    def due(self, current_day: int) -> list[BufferEntry]:
        return [e for e in self._entries.values() if e.status == "pending" and e.expected_label_day <= current_day]

    def fulfill(self, campaign_id: str, actual_label: int) -> BufferEntry:
        entry = self._entries[campaign_id]
        entry.status = "fulfilled"
        entry.actual_label = actual_label
        return entry

    def fulfilled_count(self, tenant_id: int) -> int:
        return sum(1 for e in self._entries.values() if e.status == "fulfilled" and e.tenant_id == tenant_id)

    def drain_fulfilled(self, tenant_id: int) -> list[BufferEntry]:
        drained = [e for e in self._entries.values() if e.status == "fulfilled" and e.tenant_id == tenant_id]
        for e in drained:
            e.status = "consumed"
        return drained

    def pending_count(self) -> int:
        return sum(1 for e in self._entries.values() if e.status == "pending")
