from __future__ import annotations

from fastapi import FastAPI

from fl_marketing.api.routes import audit, feedback, predict

app = FastAPI(title="FL Marketing Prediction Service")
app.include_router(predict.router)
app.include_router(feedback.router)
app.include_router(audit.router)
