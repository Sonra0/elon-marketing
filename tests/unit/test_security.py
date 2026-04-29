from elon.core.security import create_jwt, decode_jwt, decrypt_secret, encrypt_secret


def test_secret_box_roundtrip():
    plaintext = "hunter2 | refresh_xyz"
    enc = encrypt_secret(plaintext)
    assert enc != plaintext
    assert decrypt_secret(enc) == plaintext


def test_secret_box_nonce_uniqueness():
    a = encrypt_secret("hello")
    b = encrypt_secret("hello")
    assert a != b  # nonce differs each call


def test_jwt_roundtrip():
    tok = create_jwt("user-123", {"tenant_id": "t-1", "role": "owner"})
    payload = decode_jwt(tok)
    assert payload["sub"] == "user-123"
    assert payload["tenant_id"] == "t-1"
    assert payload["role"] == "owner"
    assert payload["exp"] > payload["iat"]
