from fl_marketing.core.adaptation.buffer import DelayedLabelBuffer
from fl_marketing.core.adaptation.matcher import match_label


def test_due_respects_arrival_day():
    buf = DelayedLabelBuffer()
    buf.register("c1", tenant_id=0, prediction=0.7, day=0, expected_day=10)
    assert buf.due(current_day=5) == []
    due = buf.due(current_day=10)
    assert len(due) == 1 and due[0].campaign_id == "c1"


def test_fulfill_and_count_and_drain():
    buf = DelayedLabelBuffer()
    buf.register("c1", tenant_id=0, prediction=0.7, day=0, expected_day=10)
    buf.register("c2", tenant_id=0, prediction=0.3, day=0, expected_day=12)
    match_label(buf, "c1", actual_label=1)
    match_label(buf, "c2", actual_label=0)
    assert buf.fulfilled_count(0) == 2
    drained = buf.drain_fulfilled(0)
    assert len(drained) == 2
    assert buf.fulfilled_count(0) == 0


def test_match_unknown_campaign_returns_none():
    buf = DelayedLabelBuffer()
    assert match_label(buf, "missing", actual_label=1) is None
