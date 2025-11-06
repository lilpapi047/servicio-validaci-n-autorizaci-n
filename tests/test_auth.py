import datetime as dt

def test_signup_happy_path(client):
    payload = {
        "email": "fan@example.com",
        "password": "StrongP@ssw0rd!",
        "first_name": "Fan",
        "last_name": "User",
        "date_of_birth": "1990-01-01",
        "country_code": "US",
        "phone": None
    }
    r = client.post("/auth/signup", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == payload["email"]
    assert data["is_verified"] is False


def test_signup_duplicate_email(client):
    p = {
        "email": "dup@example.com",
        "password": "Xx!234567",
        "first_name": "A",
        "last_name": "B",
        "date_of_birth": "2000-02-02",
        "country_code": "US",
        "phone": None
    }
    r1 = client.post("/auth/signup", json=p)
    assert r1.status_code == 200

    r2 = client.post("/auth/signup", json=p)
    assert r2.status_code in (400, 409) 