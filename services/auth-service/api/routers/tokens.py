from fastapi import APIRouter, HTTPException
import security

router = APIRouter()

@router.get("/verify-token")
def verify_token(token: str):
    try:
        payload = security.decode_access_token(token)
        return {"valid": True, "payload": payload}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")