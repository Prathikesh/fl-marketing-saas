from __future__ import annotations

from pydantic import BaseModel


class PredictRequest(BaseModel):
    campaign_id: str
    tenant_id: int
    features: dict


class PredictResponse(BaseModel):
    campaign_id: str
    conversion_probability: float


class FeedbackRequest(BaseModel):
    campaign_id: str
    converted: int


class FeedbackResponse(BaseModel):
    status: str
