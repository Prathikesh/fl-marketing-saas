from __future__ import annotations

from fastapi import APIRouter

from fl_marketing.api.schemas import PredictRequest, PredictResponse

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    raise NotImplementedError
