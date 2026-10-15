from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

RESULTS_FILE = Path("experiments/results/results.json")


@router.get("/results")
def results() -> dict:
    if not RESULTS_FILE.exists():
        raise HTTPException(status_code=404, detail="results artifact not found")
    return json.loads(RESULTS_FILE.read_text())
