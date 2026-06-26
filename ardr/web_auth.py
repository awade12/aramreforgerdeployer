from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path


def ensure_auth(path: Path, password: str | None) -> str | None:
    if password:
        _write_auth(path, password)
        return None
    if path.exists():
        return None
    generated = secrets.token_urlsafe(18)
    _write_auth(path, generated)
    return generated


def verify_password(path: Path, password: str) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    salt = base64.b64decode(data["salt"])
    expected = base64.b64decode(data["hash"])
    actual = _hash(password, salt)
    return hmac.compare_digest(actual, expected)


def make_session(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    nonce = secrets.token_urlsafe(24)
    expires = str(int(time.time()) + 86400)
    body = f"{expires}.{nonce}"
    sig = hmac.new(data["secret"].encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def valid_session(path: Path, value: str | None) -> bool:
    if not value or not path.exists():
        return False
    try:
        expires, nonce, sig = value.split(".", 2)
    except ValueError:
        return False
    if int(expires) < int(time.time()) or not nonce:
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    body = f"{expires}.{nonce}"
    expected = hmac.new(data["secret"].encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


def make_csrf() -> str:
    return secrets.token_urlsafe(24)


def _write_auth(path: Path, password: str) -> None:
    salt = secrets.token_bytes(16)
    path.write_text(
        json.dumps(
            {
                "salt": base64.b64encode(salt).decode(),
                "hash": base64.b64encode(_hash(password, salt)).decode(),
                "secret": secrets.token_urlsafe(32),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    path.chmod(0o600)


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)

