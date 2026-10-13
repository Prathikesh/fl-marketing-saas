from __future__ import annotations

import torch

from fastapi import APIRouter

from fl_marketing.api.dependencies import get_state
from fl_marketing.api.schemas import PredictRequest, PredictResponse
from fl_marketing.data.features import encode_record

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    state = get_state()
    vec = encode_record(request.model_dump(), state.numeric_stats, state.feature_cols)
    with torch.no_grad():
        prob = float(torch.sigmoid(state.model(torch.tensor(vec).unsqueeze(0))).item())
    predicted = int(prob >= state.threshold)
    state.buffer.register(request.campaign_id, request.tenant_id, prob, request.launch_day, request.launch_day + 14)
    return PredictResponse(
        campaign_id=request.campaign_id,
        conversion_probability=round(prob, 4),
        predicted_converted=predicted,
        threshold=round(state.threshold, 4),
    )
