import datetime as dt
from .conftest import _make_user, _make_match


def test_eligibility_email_not_verified(client, db):
    u = _make_user(db, email="nov@example.com", verified=False)
    m = _make_match(db)
    r = client.get(f"/raffle/eligibility?user_id={u.id}&match_id={m.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["eligible"] is False
    assert "Email not verified" in body["reasons"]


def test_eligibility_age_ok_and_verified(client, db):
    u = _make_user(db, email="ok@example.com", verified=True, dob=dt.date(1990, 1, 1))
    m = _make_match(db)
    r = client.get(f"/raffle/eligibility?user_id={u.id}&match_id={m.id}")
    assert r.status_code == 200
    body = r.json()
    assert body["eligible"] is True
