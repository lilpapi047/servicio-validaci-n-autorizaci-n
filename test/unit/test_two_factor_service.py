from API.app.services import two_factor_service
import pyotp

def test_generate_and_verify_otp():
    secret = two_factor_service.generate_2fa_secret()
    totp = pyotp.TOTP(secret)
    token = totp.now()  # genera un código válido en este instante
    assert two_factor_service.verify_2fa_token(secret, token) is True
