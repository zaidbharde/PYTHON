import hmac
import hashlib
import base64
import json

SECRET = b"foresight-secret-key"

def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def create_token(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    header_enc = b64url_encode(json.dumps(header).encode())
    payload_enc = b64url_encode(json.dumps(payload).encode())
    signing_input = f"{header_enc}.{payload_enc}".encode()
    signature = hmac.new(SECRET, signing_input, hashlib.sha256).digest()
    sig_enc = b64url_encode(signature)
    return f"{header_enc}.{payload_enc}.{sig_enc}"

def verify_token(token):
    header_enc, payload_enc, sig_enc = token.split(".")
    signing_input = f"{header_enc}.{payload_enc}".encode()
    expected_sig = hmac.new(SECRET, signing_input, hashlib.sha256).digest()
    actual_sig = b64url_decode(sig_enc)
    if not hmac.compare_digest(expected_sig, actual_sig):
        return None
    return json.loads(b64url_decode(payload_enc))


if __name__ == "__main__":
    token = create_token({"user": "zaidbharde", "role": "intern"})
    print("Token:", token)
    print("Verified:", verify_token(token))
