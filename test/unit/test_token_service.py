from API.app.services import token_service

def test_generate_and_validate_token():
    email = "nohelyreyes033@gmail.com"
    token = token_service.generate_verification_token(email)
    assert token_service.validate_verification_token(token) is True
