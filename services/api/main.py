from fastapi import FastAPI
from .routers import auth, eligibility, user, match, raffle

app = FastAPI(title="Global Cup Ticket API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(eligibility.router, prefix="/raffle", tags=["raffle"])