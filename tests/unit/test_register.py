def test_register_user(client):
    payload = {
        "email": "test@test.com",
        "password": "password123",
        "first_name": "test",
        "last_name": "test"
    }

    response = client.post("/register", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert "id" in data
    assert data["email"] == payload["email"]


def test_register_duplicate_email(client):
    payload = {
        "email": "test@test.com",
        "password": "password123",
        "first_name": "test"
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 409