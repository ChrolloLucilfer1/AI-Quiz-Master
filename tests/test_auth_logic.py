import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import auth_logic


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Point auth_logic at a throwaway DB file for every test."""
    db_file = tmp_path / "test_users.db"
    monkeypatch.setattr(auth_logic, "DB_PATH", str(db_file))
    auth_logic.init_db()
    yield


def test_hash_password_is_deterministic():
    h1 = auth_logic.hash_password("mypassword")
    h2 = auth_logic.hash_password("mypassword")
    assert h1 == h2


def test_hash_password_differs_for_different_input():
    assert auth_logic.hash_password("a") != auth_logic.hash_password("b")


def test_add_user_succeeds_for_new_user():
    assert auth_logic.add_user("alice", "secret123") is True


def test_add_user_fails_for_duplicate_username():
    auth_logic.add_user("bob", "pass1")
    assert auth_logic.add_user("bob", "pass2") is False


def test_add_user_rejects_empty_username_or_password():
    assert auth_logic.add_user("", "pass") is False
    assert auth_logic.add_user("user", "") is False


def test_login_succeeds_with_correct_credentials():
    auth_logic.add_user("carol", "rightpass")
    result = auth_logic.login_user("carol", "rightpass")
    assert result is not None


def test_login_fails_with_wrong_password():
    auth_logic.add_user("dave", "rightpass")
    result = auth_logic.login_user("dave", "wrongpass")
    assert result is None


def test_login_fails_for_nonexistent_user():
    result = auth_logic.login_user("ghost", "whatever")
    assert result is None
