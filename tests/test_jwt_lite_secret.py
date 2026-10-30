import unittest

from jwt_lite import create_token, verify_token


class JwtSecretTests(unittest.TestCase):
    KEY = bytes(range(32))
    OTHER_KEY = bytes(range(1, 33))

    def test_round_trip_requires_explicit_strong_secret(self):
        payload = {"user": "alice", "role": "reader"}
        token = create_token(payload, self.KEY)
        self.assertEqual(verify_token(token, self.KEY), payload)
        with self.assertRaises(TypeError):
            create_token(payload)
        with self.assertRaises(ValueError):
            create_token(payload, b"short")

    def test_wrong_key_and_malformed_token_are_rejected(self):
        token = create_token({"user": "alice"}, self.KEY)
        self.assertIsNone(verify_token(token, self.OTHER_KEY))
        self.assertIsNone(verify_token("not-a-token", self.KEY))
        self.assertIsNone(verify_token(None, self.KEY))

    def test_non_hs256_header_is_rejected(self):
        token = create_token({"user": "alice"}, self.KEY)
        header, payload, signature = token.split(".")
        import base64
        import json
        from jwt_lite import b64url_encode

        forged_header = b64url_encode(json.dumps({"alg": "none", "typ": "JWT"}).encode())
        self.assertIsNone(verify_token(f"{forged_header}.{payload}.{signature}", self.KEY))


if __name__ == "__main__":
    unittest.main()
