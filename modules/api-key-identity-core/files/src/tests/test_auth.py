"""Unit tests for API key hashing and generation."""

from db.auth import generate_api_key, hash_api_key


def test_generate_api_key_returns_unique_non_empty_strings() -> None:
    a = generate_api_key()
    b = generate_api_key()
    assert a
    assert b
    assert a != b


def test_hash_api_key_is_deterministic_for_same_input() -> None:
    salt = "test-salt"
    assert hash_api_key("my-key", salt=salt) == hash_api_key("my-key", salt=salt)


def test_hash_api_key_changes_with_different_key_or_salt() -> None:
    salt = "test-salt"
    a = hash_api_key("key-a", salt=salt)
    b = hash_api_key("key-b", salt=salt)
    c = hash_api_key("key-a", salt="other-salt")
    assert a != b
    assert a != c
