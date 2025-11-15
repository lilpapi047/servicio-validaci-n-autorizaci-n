from fastapi import FastAPI
from .routers import auth, eligibility, user, match, raffle, criteria
import os
from .database import Base, engine


app = FastAPI(title="Global Cup Ticket API")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(eligibility.router, prefix="/raffle", tags=["raffle"])
app.include_router(raffle.router, prefix="/raffle", tags=["raffle"])
app.include_router(criteria.router)

@app.on_event("startup")
def ensure_tables():
    Base.metadata.create_all(bind=engine)