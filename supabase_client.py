
# supabase_client.py
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from typing import Optional

# Load environment variables
load_dotenv()

# --- Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ANON_KEY = os.getenv("SUPABASE_ANON_KEY") 

# Check for critical values
if not SUPABASE_URL:
    raise EnvironmentError("Missing SUPABASE_URL in env")
if not SERVICE_KEY:
    raise EnvironmentError("Missing SUPABASE_SERVICE_ROLE_KEY in env")
if not ANON_KEY:
    # This is a warning, as RLS-enforced operations will fail without it
    print("Warning: SUPABASE_ANON_KEY missing. RLS-enforcing client cannot be initialized.")


# --------------------------------------------------------------------------
# 1. SERVICE ROLE CLIENT (Admin/Bypasses RLS)
#    - Use this ONLY for privileged, server-to-server operations (like /sync-sheet upsert).
# --------------------------------------------------------------------------
service_role_client: Client = create_client(SUPABASE_URL, SERVICE_KEY)


# --------------------------------------------------------------------------
# 2. RLS-ENFORCING CLIENT (User/Respects RLS)
#    - Use this for all user-facing reads/writes. Requires a JWT token to be set.
# --------------------------------------------------------------------------
rls_enforcing_client: Optional[Client] = None
if ANON_KEY:
    rls_enforcing_client = create_client(SUPABASE_URL, ANON_KEY)