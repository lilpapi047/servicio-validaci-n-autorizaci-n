import pytest
from servicio_validacion.app.services import email_service

@pytest.fixture(autouse=True)
def mock_resend(monkeypatch):
    """Simula el envío de correo sin usar la API real de Resend."""
    def fake_send(data):
        print(f"📩 Simulando envío de correo a: {data['to']}")
        return {"status": "sent"}

    monkeypatch.setattr("resend.Emails.send", fake_send)

def test_send_verification_email():
    """Prueba que el correo de verificación se envíe correctamente."""
    result = email_service.send_verification_email(
        "nohelyreyes033@gmail.com",
        "http://localhost:5173/verify?token=abc123"
    )
    assert result is True
