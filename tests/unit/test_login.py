def test_login_success(client):
    # Primero crear el usuario
    register_payload = {
        "email": "unique1@test.com",
        "password": "password123"
    }
    client.post("/register", json=register_payload)

    # Luego intentar login
    login_payload = {
        "email": "unique1@test.com",
        "password": "password123"
    }

    response = client.post("/login", json=login_payload)
    data = response.json()

    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    payload = {
        "email": "unique1@test.com",
        "password": "wrongpassword"
    }

    response = client.post("/login", json=payload)
    assert response.status_code == 401