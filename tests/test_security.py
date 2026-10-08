def test_password():
    from services.security.password_service import hash_password,verify_password
    p=hash_password("Test@12345"); assert verify_password("Test@12345",p)
