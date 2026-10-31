import base64
import binascii
import hashlib
import hmac
import json
import re
import secrets


def _secret_bytes(secret):
    """Return a caller-provided HS256 key of at least 256 bits."""
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    if not isinstance(secret, bytes):
        raise TypeError("secret must be bytes or str")
    if len(secret) < 32:
        raise ValueError("secret must contain at least 32 bytes")
    return secret


def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(data):
    if not isinstance(data, str) or re.fullmatch(r"[A-Za-z0-9_-]*", data) is None:
        raise ValueError("invalid base64url data")
    padding = "=" * (-len(data) % 4)
    return base64.b64decode(data + padding, altchars=b"-_", validate=True)


def create_token(payload, secret):
    """Create an HS256 token using an explicit, strong secret key."""
    key = _secret_bytes(secret)
    header_enc = b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload_enc = b64url_encode(json.dumps(payload).encode())
    signing_input = f"{header_enc}.{payload_enc}".encode("ascii")
    signature = hmac.new(key, signing_input, hashlib.sha256).digest()
    return f"{header_enc}.{payload_enc}.{b64url_encode(signature)}"


def verify_token(token, secret):
    """Return the decoded payload when a valid HS256 signature is supplied."""
    key = _secret_bytes(secret)
    if not isinstance(token, str):
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    header_enc, payload_enc, signature_enc = parts
    try:
        header = json.loads(b64url_decode(header_enc))
        if not isinstance(header, dict) or header.get("alg") != "HS256":
            return None
        signing_input = f"{header_enc}.{payload_enc}".encode("ascii")
        expected = hmac.new(key, signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, b64url_decode(signature_enc)):
            return None
        return json.loads(b64url_decode(payload_enc))
    except (ValueError, TypeError, UnicodeDecodeError, binascii.Error):
        return None


if __name__ == "__main__":
    demo_secret = secrets.token_bytes(32)
    token = create_token({"user": "zaidbharde", "role": "intern"}, demo_secret)
    print("Token:", token)
    print("Verified:", verify_token(token, demo_secret))
