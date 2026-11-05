"""Local prototype analyst accounts and role-based permissions.

This is a demonstration login system, not production authentication. Passwords
are hashed with PBKDF2; credentials must be configured locally and never committed.
"""
import hashlib
import hmac
import os
import secrets
from pathlib import Path

ROLES = {"viewer", "analyst", "admin"}
ITERATIONS = 310_000
DEFAULT_USERS_FILE = Path(__file__).resolve().parents[1] / "data" / "analysts.json"


def hash_password(password, salt=None):
    if not isinstance(password, str) or len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return {"salt": salt.hex(), "hash": digest.hex(), "iterations": ITERATIONS}


def verify_password(password, record):
    try:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(),
            bytes.fromhex(record["salt"]), int(record["iterations"]))
        return hmac.compare_digest(digest.hex(), record["hash"])
    except (ValueError, TypeError, KeyError):
        return False


def load_users(path=DEFAULT_USERS_FILE):
    import json
    file_path = Path(path)
    if not file_path.exists():
        return {}
    return json.loads(file_path.read_text(encoding="utf-8"))


def save_users(users, path=DEFAULT_USERS_FILE):
    import json
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(users, indent=2), encoding="utf-8")
    try:
        os.chmod(file_path, 0o600)
    except OSError:
        pass


def create_user(username, password, role="analyst", path=DEFAULT_USERS_FILE):
    username = str(username).strip()
    if not username or len(username) > 64:
        raise ValueError("Username must be 1–64 characters")
    if role not in ROLES:
        raise ValueError("Invalid role")
    users = load_users(path)
    if username in users:
        raise ValueError("Username already exists")
    users[username] = {**hash_password(password), "role": role}
    save_users(users, path)
    return {"username": username, "role": role}


def authenticate(username, password, path=DEFAULT_USERS_FILE):
    record = load_users(path).get(str(username).strip())
    if not record or not verify_password(password, record):
        return None
    return {"username": str(username).strip(), "role": record["role"]}


def can(permission, role):
    rules = {
        "view": {"viewer", "analyst", "admin"},
        "review": {"analyst", "admin"},
        "manage_users": {"admin"},
    }
    return role in rules.get(permission, set())
