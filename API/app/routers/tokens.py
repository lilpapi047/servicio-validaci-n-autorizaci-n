from fastapi import APIRouter, HTTPException
from app import security

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/verify-token")
def verify_token(token: str):
    try:
        payload = security.decode_access_token(token)
        return {"valid": True, "payload": payload}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")