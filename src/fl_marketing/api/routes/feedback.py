from __future__ import annotations

from fastapi import APIRouter

from fl_marketing.api.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(request: FeedbackRequest) -> FeedbackResponse:
    raise NotImplementedError
