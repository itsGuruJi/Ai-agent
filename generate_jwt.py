# generate_jwt.py
import jwt
import datetime
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# --- Configuration ---
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_JWT_SECRET:
    raise EnvironmentError(
        "SUPABASE_JWT_SECRET environment variable is missing. "
        "This is required for generating RLS-compatible tokens."
    )

def generate_custom_jwt(
    user_id: str,
    email: str,
    org_id: str,
    role: str = "authenticated",
    expiry_hours: int = 1,
    custom_claims: Optional[Dict[str, Any]] = None
) -> str:
    """Generates a JWT token signed with the Supabase JWT Secret."""
    current_time = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id), 
        "email": email,
        "role": role, 
        "org_id": org_id, # Custom claim for your API/RLS logic
        "exp": current_time + datetime.timedelta(hours=expiry_hours),
        "iat": current_time,
        "nbf": current_time
    }
    
    if custom_claims:
        payload.update(custom_claims)

    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    return token

# --- Example Usage (for testing only) ---
if __name__ == "__main__":
    try:
        test_token = generate_custom_jwt(
            user_id="user_123",
            email="test@example.com",
            org_id="org_001",
        )
        print("\n✅ GENERATED TEST TOKEN (Use for API Authorization):\n")
        print(test_token)
    except EnvironmentError as e:
        print(f"Error: {e}")