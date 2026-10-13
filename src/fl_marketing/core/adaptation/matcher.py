from __future__ import annotations

from fl_marketing.core.adaptation.buffer import BufferEntry, DelayedLabelBuffer


def match_label(buffer: DelayedLabelBuffer, campaign_id: str, actual_label: int) -> BufferEntry | None:
    try:
        return buffer.fulfill(campaign_id, actual_label)
    except KeyError:
        return None
