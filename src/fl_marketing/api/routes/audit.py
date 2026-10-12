from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/audit")
def audit() -> list[dict]:
    raise NotImplementedError
