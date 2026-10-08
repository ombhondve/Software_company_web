import time

from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password():
    h = hash_password("secret-pass")
    assert h != "secret-pass"
    assert verify_password("secret-pass", h)
    assert not verify_password("wrong", h)


def test_verify_password_with_garbage_hash():
    assert not verify_password("x", "not-a-bcrypt-hash")


def test_token_roundtrip():
    assert decode_access_token(create_access_token(42)) == 42


def test_invalid_token_returns_none():
    assert decode_access_token("garbage") is None


def test_expired_token_returns_none():
    token = create_access_token(1, expires_minutes=-1)
    time.sleep(0.01)
    assert decode_access_token(token) is None
