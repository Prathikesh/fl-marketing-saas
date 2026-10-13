from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fl_marketing.api.routes import audit, feedback, predict

app = FastAPI(title="FL Marketing Prediction Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(feedback.router)
app.include_router(audit.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
