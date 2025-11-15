from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from ..database import get_db
from .. import models
from ..eligibility_rules import evaluate_eligibility

router = APIRouter()

class EligibilityResponse(BaseModel):
    eligible: bool
    reasons: list[str]

@router.get("/eligibility", response_model=EligibilityResponse)
def check_eligibility(
    user_id: int = Query(..., ge=1),
    match_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    match = db.get(models.Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")

    min_age = int(os.getenv("MIN_ELIGIBILITY_AGE", "18"))
    ok, reasons = evaluate_eligibility(db, user, match, min_age)
    return EligibilityResponse(eligible=ok, reasons=reasons)
