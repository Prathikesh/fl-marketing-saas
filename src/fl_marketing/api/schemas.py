from __future__ import annotations

from pydantic import BaseModel


class PredictRequest(BaseModel):
    campaign_id: str = "demo-1"
    tenant_id: int = 0
    lead_origin: str = "API"
    last_activity: str = "Email Opened"
    occupation: str = "Unemployed"
    specialization: str = "Unknown"
    city: str = "Mumbai"
    last_notable_activity: str = "Modified"
    do_not_email: int = 0
    free_copy: int = 0
    total_visits: float = 3
    time_on_site: float = 500
    page_views_per_visit: float = 2.5
    activity_score: float = 15
    profile_score: float = 16
    launch_day: int = 0


class PredictResponse(BaseModel):
    campaign_id: str
    conversion_probability: float
    predicted_converted: int
    threshold: float


class FeedbackRequest(BaseModel):
    campaign_id: str
    converted: int


class FeedbackResponse(BaseModel):
    campaign_id: str
    status: str
    tenant_fulfilled_count: int
