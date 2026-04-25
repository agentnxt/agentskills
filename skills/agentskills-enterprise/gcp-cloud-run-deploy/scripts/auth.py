#!/usr/bin/env python3
"""
OAuth2 token exchange for GCP service account.
Exchanges a service account JSON key for a bearer token via the Google OAuth2 API.

Usage:
    python auth.py --key-file /path/to/sa-key.json
    python auth.py --key-file /path/to/sa-key.json --scope https://www.googleapis.com/auth/cloud-platform
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import hashlib
import hmac
import base64

# --- Minimal JWT implementation (no external dependencies) ---

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def _create_jwt(payload: dict, private_key_pem: str) -> str:
    """Create a signed JWT using RS256. Requires the cryptography library if available,
    otherwise falls back to subprocess openssl."""
    header = {"alg": "RS256", "typ": "JWT"}
    segments = [
        _b64url_encode(json.dumps(header).encode()),
        _b64url_encode(json.dumps(payload).encode())
    ]
    signing_input = '.'.join(segments).encode()

    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(), password=None
        )
        signature = private_key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    except ImportError:
        import subprocess
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as f:
            f.write(private_key_pem)
            key_path = f.name
        try:
            result = subprocess.run(
                ['openssl', 'dgst', '-sha256', '-sign', key_path],
                input=signing_input, capture_output=True
            )
            signature = result.stdout
        finally:
            os.unlink(key_path)

    segments.append(_b64url_encode(signature))
    return '.'.join(segments)

# --- Token exchange ---

def get_access_token(
    key_file: str,
    scopes: str = "https://www.googleapis.com/auth/cloud-platform"
) -> dict:
    """Exchange a service account key for an access token.

    Returns dict with 'access_token', 'expires_in', 'token_type'.
    """
    with open(key_file) as f:
        key_data = json.load(f)

    now = int(time.time())
    payload = {
        "iss": key_data["client_email"],
        "scope": scopes,
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600
    }

    signed_jwt = _create_jwt(payload, key_data["private_key"])

    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": signed_jwt
    }).encode()

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read())
            return {
                "access_token": token_data["access_token"],
                "expires_in": token_data.get("expires_in", 3600),
                "token_type": token_data.get("token_type", "Bearer"),
                "service_account": key_data["client_email"],
                "project_id": key_data.get("project_id", "unknown")
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error exchanging token: {e.code} {error_body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Get GCP OAuth2 access token from service account key")
    parser.add_argument("--key-file", required=True, help="Path to service account JSON key file")
    parser.add_argument("--scope", default="https://www.googleapis.com/auth/cloud-platform",
                        help="OAuth2 scope (default: cloud-platform)")
    parser.add_argument("--json", action="store_true", help="Output full JSON response")
    args = parser.parse_args()

    result = get_access_token(args.key_file, args.scope)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["access_token"])


if __name__ == "__main__":
    main()
