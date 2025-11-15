from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json, os
from ..database import get_db
from .. import models

router = APIRouter(prefix="/criteria", tags=["eligibility-criteria"])

ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN", "")

def require_admin(authorization: str = Header(None)):
    if not ADMIN_API_TOKEN:
        raise HTTPException(500, "ADMIN_API_TOKEN not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    token = authorization.split(" ", 1)[1]
    if token != ADMIN_API_TOKEN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")

class CriterionOut(BaseModel):
    id: int
    key: str
    name: str
    description: str | None = None
    active: bool
    value_int: int | None = None

class CriterionPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    active: bool | None = None
    value_int: int | None = None

@router.get("/", response_model=list[CriterionOut])
def list_criteria(db: Session = Depends(get_db)):
    rows = db.query(models.EligibilityCriterion).order_by(models.EligibilityCriterion.key).all()
    return [CriterionOut(
        id=r.id, key=r.key, name=r.name, description=r.description, active=r.active, value_int=r.value_int
    ) for r in rows]

@router.patch("/{criterion_id}", response_model=CriterionOut, dependencies=[Depends(require_admin)])
def update_criterion(criterion_id: int, patch: CriterionPatch, db: Session = Depends(get_db)):
    r = db.get(models.EligibilityCriterion, criterion_id)
    if not r:
        raise HTTPException(404, "Criterion not found")

    before = {
        "name": r.name, "description": r.description, "active": r.active, "value_int": r.value_int
    }

    if patch.name is not None: r.name = patch.name
    if patch.description is not None: r.description = patch.description
    if patch.active is not None: r.active = patch.active
    if patch.value_int is not None: r.value_int = patch.value_int

    db.add(r); db.commit(); db.refresh(r)

    after = {
        "name": r.name, "description": r.description, "active": r.active, "value_int": r.value_int
    }

    audit = models.EligibilityAudit(
        actor="admin:token", action="update", criterion_id=r.id,
        before_json=json.dumps(before), after_json=json.dumps(after)
    )
    db.add(audit); db.commit()

    return CriterionOut(
        id=r.id, key=r.key, name=r.name, description=r.description, active=r.active, value_int=r.value_int
    )

@router.get("/audit", dependencies=[Depends(require_admin)])
def list_audit(db: Session = Depends(get_db), limit: int = 100):
    q = db.query(models.EligibilityAudit).order_by(models.EligibilityAudit.at.desc()).limit(limit).all()
    # Devuelve las filas
    return [
        {
            "id": a.id, "actor": a.actor, "action": a.action, "criterion_id": a.criterion_id,
            "before": json.loads(a.before_json) if a.before_json else None,
            "after": json.loads(a.after_json) if a.after_json else None,
            "at": a.at
        } for a in q
    ]
