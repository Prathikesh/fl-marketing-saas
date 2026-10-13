from __future__ import annotations

from fastapi import APIRouter

from fl_marketing.api.dependencies import get_state

router = APIRouter()


@router.get("/audit")
def audit() -> dict:
    state = get_state()
    return {
        "differential_privacy": state.private,
        "federated_rounds": state.audit,
        "buffer_pending": state.buffer.pending_count(),
    }


@router.get("/tenants")
def tenants() -> dict:
    return get_state().tenants
