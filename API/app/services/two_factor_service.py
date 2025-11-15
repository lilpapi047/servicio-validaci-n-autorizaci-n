import pyotp

def generate_2fa_secret() -> str:
    """
    Genera una clave secreta para la autenticación de dos factores (2FA).
    """
    return pyotp.random_base32()

def verify_2fa_token(secret: str, token: str) -> bool:
    """
    Verifica si el token 2FA proporcionado es válido para la clave secreta.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
