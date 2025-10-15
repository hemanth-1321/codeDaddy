import os
import time
import jwt
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization

load_dotenv()

# Load GitHub App ID
github_app_id_str = os.getenv("MY_GITHUB_APP_ID")
if not github_app_id_str:
    raise RuntimeError("❌ GITHUB_APP_ID environment variable is not set")
GITHUB_APP_ID = int(github_app_id_str)

# Load GitHub Private Key
raw_key = os.getenv("MY_GITHUB_PRIVATE_KEY")
if not raw_key:
    raise RuntimeError("❌ GITHUB_PRIVATE_KEY environment variable is not set")

# Replace escaped \n with real newlines (if using single-line env format)
GITHUB_PRIVATE_KEY = raw_key.replace("\\n", "\n").strip()

# Debug: show beginning and end of key
print("🔑 Key starts with:", GITHUB_PRIVATE_KEY[:40])
print("🔑 Key ends with:", GITHUB_PRIVATE_KEY[-40:])

# Validate PEM format
try:
    serialization.load_pem_private_key(
        GITHUB_PRIVATE_KEY.encode(),
        password=None,
    )
    print("✅ Private key is valid PEM")
except Exception as e:
    raise RuntimeError(f"❌ Invalid private key format: {e}")

def generate_app_jwt():
    """Generate a GitHub App JWT using RS256"""
    payload = {
        "iat": int(time.time()) - 60,          # issued at (backdate 60s to allow clock drift)
        "exp": int(time.time()) + (10 * 60),   # expires in 10 minutes
        "iss": GITHUB_APP_ID
    }
    return jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm="RS256")

def get_installations_headers():
    return {
        "Authorization": f"Bearer {generate_app_jwt()}",
        "Accept": "application/vnd.github+json"
    }
