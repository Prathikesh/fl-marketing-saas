from __future__ import annotations

from fastapi import APIRouter

from fl_marketing.api.dependencies import get_state
from fl_marketing.api.schemas import FeedbackRequest, FeedbackResponse
from fl_marketing.core.adaptation.matcher import match_label

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    state = get_state()
    entry = match_label(state.buffer, request.campaign_id, request.converted)
    if entry is None:
        return FeedbackResponse(campaign_id=request.campaign_id, status="unknown_campaign", tenant_fulfilled_count=0)
    return FeedbackResponse(
        campaign_id=request.campaign_id,
        status="label_matched",
        tenant_fulfilled_count=state.buffer.fulfilled_count(entry.tenant_id),
    )
