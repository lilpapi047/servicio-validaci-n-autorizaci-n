"""
Legacy script moved here for manual runs. This file no longer runs at import
time to avoid pytest collection errors. To run the script manually:

    python test_perfil.py

The script only executes when run as __main__.
"""

if __name__ == "__main__":
    # Lightweight manual runner preserved for convenience.
    # Import inside guard to avoid pytest collecting and executing TestClient
    import sys
    import uuid
    from fastapi.testclient import TestClient
    from main import app
    from services.api.database import Base, engine

    Base.metadata.create_all(bind=engine)
    client = TestClient(app)

    def run_manual():
        email_test = f"juan_{uuid.uuid4().hex[:8]}@example.com"
        user_data = {
            "email": email_test,
            "hash_pwd": "password123",
            "first_name": "Juan",
            "last_name": "Perez",
            "country_code": "CO",
            "phone": "3001234567"
        }
        r = client.post("/api/registro", json=user_data)
        print("Manual run - status:", r.status_code)

    try:
        run_manual()
    except Exception as e:
        print("Error during manual run:", e)
        sys.exit(1)
