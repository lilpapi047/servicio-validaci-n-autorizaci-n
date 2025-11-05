import secrets
import time

def generate_verification_token(email: str) -> str:

    return f"{email}-{secrets.token_hex(16)}-{int(time.time())}"

def validate_verification_token(token: str) -> bool:
  
    return token.count('-') >= 2
