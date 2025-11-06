import datetime as dt
from sqlalchemy.orm import Session
from services.api import models

def _make_user(db: Session, *, email="u@example.com", dob=dt.date(1990,1,1), verified=False):
    u = models.User(
        email=email,
        hash_pwd="not_used_in_tests",
        is_verified=verified,
        first_name="X",
        last_name="Y",
        date_of_birth=dob,
        country_code="US",
        phone=None,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def test_eligibility_email_not_verified(client, db):
    u = _make_user(db, email="nov@example.com", verified=False)
    r = client.get(f"/raffle/eligibility?user_id={u.id}&match_id=1")
    assert r.status_code == 200
    body = r.json()
    assert body["eligible"] is False
    assert any("Email not verified" in s for s in body["reasons"])

def test_eligibility_age_ok_and_verified(client, db):
    u = _make_user(db, email="ok@example.com", verified=True, dob=dt.date(1990,1,1))
    r = client.get(f"/raffle/eligibility?user_id={u.id}&match_id=1")
    assert r.status_code == 200
    body = r.json()


    assert body["eligible"] is True
