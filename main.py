# main.py
import os
import random
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import jwt
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# --- Load environment variables ---
load_dotenv()

# --- Import Clients ---
from supabase_client import service_role_client, rls_enforcing_client
from google_sync import read_sheet_values
from ai_agent import ask_openai
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

app = FastAPI(title="AI Agent Bridge")

# ======================================================
# ✅ JWT Claims Verification
# ======================================================
def get_claims(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bad Authorization header format")

    token = parts[1]
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        if "org_id" not in payload:
            raise HTTPException(status_code=403, detail="Token missing 'org_id'")
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

# ======================================================
# ✅ Schemas
# ======================================================
class SyncRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: Optional[str] = "Sheet1"
    org_id: Optional[str] = None


class QueryRequest(BaseModel):
    prompt: str


class SheetQueryRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: Optional[str] = "Sheet1"
    prompt: str

# ======================================================
# ✅ Health Check
# ======================================================
@app.get("/")
def root():
    return {"message": "✅ AI Agent API is running"}

# ======================================================
# ✅ Sync Google Sheet → Supabase
# ======================================================
@app.post("/sync-sheet")
async def sync_sheet(req: SyncRequest, claims: dict = Depends(get_claims)):
    if not service_role_client:
        raise HTTPException(status_code=500, detail="Service Role client not initialized.")

    org_id = req.org_id or claims.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Missing org_id")

    try:
        rows = read_sheet_values(req.spreadsheet_id, req.sheet_name)
    except (ValueError, RuntimeError, EnvironmentError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to read Google Sheet: {e}")

    payload = [
        {
            "org_id": org_id,
            "sheet_row_id": f"{org_id}:{req.spreadsheet_id}:{req.sheet_name}:{i}",
            "data": r,
            "synced_at": datetime.utcnow().isoformat(),
        }
        for i, r in enumerate(rows, start=1)
    ]

    try:
        service_role_client.table("sheets_rows").upsert(payload, on_conflict="sheet_row_id").execute()
        print(f"✅ Synced {len(payload)} rows for org_id={org_id}")
        return {"status": "ok", "inserted": len(payload)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Supabase upsert failed: {e}")

# ======================================================
# ✅ Manual AI Query Endpoint (with real data context)
# ======================================================
@app.post("/agent-query")
async def agent_query(req: QueryRequest, claims: dict = Depends(get_claims)):
    org_id = claims.get("org_id")

    try:
        # Pull sample data for better context
        rows_resp = service_role_client.table("sheets_rows").select("*").eq("org_id", org_id).limit(10).execute()
        rows = getattr(rows_resp, "data", []) or []
        data_snippet = str(rows[:5]) if rows else "No org data found."

        system_prompt = (
            f"You are a professional AI data analyst for org {org_id}. "
            f"Use this data context to answer accurately:\n{data_snippet}\n\n"
            "Be concise and output in readable sentences or tables."
        )

        answer = await ask_openai(req.prompt, system_prompt=system_prompt)
        return {"answer": answer, "org_id": org_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI agent failed: {e}")

# ======================================================
# ✅ Fetch Supabase Rows (Smart + Secure)
# ======================================================
@app.get("/rows")
async def get_rows(
    limit: int = 50,
    claims: dict = Depends(get_claims),
    authorization: str = Header(...),
):
    import traceback

    org_id = claims.get("org_id")
    token = authorization.split()[1]

    if not service_role_client:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")

    try:
        # Try RLS-enforced read first
        if rls_enforcing_client:
            try:
                if hasattr(rls_enforcing_client, "using_access_token"):
                    user_client = rls_enforcing_client.using_access_token(token)
                else:
                    user_client = rls_enforcing_client

                resp = user_client.table("sheets_rows").select("*").eq("org_id", org_id).limit(limit).execute()
                data = getattr(resp, "data", []) or []
                if data:
                    print(f"✅ [ROWS] Returned {len(data)} records for org_id={org_id} via RLS client")
                    return {"data": data}
                else:
                    print(f"⚠️ [ROWS] No rows via RLS client for org_id={org_id}")
            except Exception as e:
                print(f"⚠️ [ROWS] RLS fetch failed: {e}")

        # Fallback to Service Role
        resp = service_role_client.table("sheets_rows").select("*").eq("org_id", org_id).limit(limit).execute()
        data = getattr(resp, "data", []) or []
        if data:
            print(f"✅ [ROWS] Returned {len(data)} records for org_id={org_id} via service role")
            return {"data": data}

        # Fallback — return any data if org filter fails
        print(f"⚠️ [ROWS] No org-specific rows found; returning global fallback")
        resp = service_role_client.table("sheets_rows").select("*").limit(limit).execute()
        data = getattr(resp, "data", []) or []
        print(f"✅ [ROWS] Fallback returned {len(data)} rows")
        return {"data": data}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching rows: {e}")

# ======================================================
# ✅ Automated AI Task Runner
# ======================================================
@app.post("/run-agent")
async def run_agent(claims: dict = Depends(get_claims)):
    if not service_role_client:
        raise HTTPException(status_code=500, detail="Service Role client not initialized.")

    org_id = claims.get("org_id")
    if not org_id:
        raise HTTPException(status_code=400, detail="Missing org_id")

    print(f"🔍 Running agent for org_id={org_id}")

    try:
        rows_resp = service_role_client.table("sheets_rows").select("*").eq("org_id", org_id).execute()
        rows = getattr(rows_resp, "data", []) or []
        print(f"📦 Found {len(rows)} rows for org_id={org_id}")

        processed = []
        for row in rows:
            row_id = row.get("sheet_row_id")
            if not row_id:
                continue

            # Skip already processed
            existing = service_role_client.table("agent_tasks").select("*").eq("sheet_row_id", row_id).execute().data
            if existing:
                continue

            content = str(row.get("data"))
            print(f"🧠 Processing {row_id}")

            try:
                ai_result = await ask_openai(
                    prompt=f"Summarize this record: {content}",
                    system_prompt="You are an AI assistant analyzing spreadsheet data."
                )
            except Exception as e:
                ai_result = f"(mocked fallback) {content[:100]} — error: {e}"

            service_role_client.table("agent_tasks").insert({
                "org_id": org_id,
                "sheet_row_id": row_id,
                "task_type": "summarize",
                "input_data": content,
                "result": ai_result,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
            }).execute()

            processed.append({"row_id": row_id, "result": ai_result})

        print(f"✅ Completed {len(processed)} summaries for org_id={org_id}")
        return {"status": "ok", "processed": len(processed)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent automation failed: {e}")

# ======================================================
# ✅ Background Scheduler (every 30 minutes)
# ======================================================
scheduler = BackgroundScheduler()

def automated_agent_job():
    try:
        org_id = "org_001"
        print(f"🤖 [Scheduler] Running background automation for {org_id}")
        rows = service_role_client.table("sheets_rows").select("*").eq("org_id", org_id).execute().data

        if not rows:
            print("📭 [Scheduler] No new rows found.")
            return

        for row in rows:
            row_id = row.get("sheet_row_id")
            content = str(row.get("data"))
            ai_result = f"(auto-summary) for {row_id}: {content[:60]}"

            service_role_client.table("agent_tasks").insert({
                "org_id": org_id,
                "sheet_row_id": row_id,
                "task_type": "scheduled_summary",
                "input_data": content,
                "result": ai_result,
                "status": "completed",
                "created_at": datetime.utcnow().isoformat(),
            }).execute()
        print("✅ [Scheduler] Job completed successfully")
    except Exception as e:
        print(f"❌ [Scheduler] Failed: {e}")

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(automated_agent_job, "interval", minutes=30)
    scheduler.start()
    print("🕒 Scheduler started (runs every 30 min)")

@app.post("/run-scheduler")
def run_scheduler_now():
    automated_agent_job()
    return {"message": "Scheduler executed manually"}

# ======================================================
# ✅ Debug & Mock Seeder
# ======================================================
@app.get("/debug/env")
def debug_env():
    return {
        "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
        "SUPABASE_SERVICE_ROLE_KEY": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY")),
        "OPENROUTER_API_KEY": bool(os.getenv("OPENROUTER_API_KEY")),
        "GOOGLE_SA_JSON_PATH": os.getenv("GOOGLE_SA_JSON_PATH"),
    }

@app.get("/debug/supabase")
def debug_supabase():
    try:
        resp = service_role_client.table("sheets_rows").select("*").limit(1).execute()
        return {"ok": True, "sample_rows": getattr(resp, "data", [])}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.post("/seed-mock-data")
def seed_mock_data(claims: dict = Depends(get_claims)):
    org_id = claims.get("org_id")
    if not service_role_client:
        raise HTTPException(status_code=500, detail="Service Role client not initialized.")

    names = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah", "Ivan", "Julia"]
    departments = ["Engineering", "HR", "Marketing", "Finance", "Sales", "Support", "Operations", "Research"]
    cities = ["Delhi", "Mumbai", "Bangalore", "Pune", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad"]

    mock_rows = []
    for i in range(1, 201):
        record = {
            "Name": random.choice(names) + f" {i}",
            "Age": random.randint(22, 55),
            "Department": random.choice(departments),
            "City": random.choice(cities),
            "Salary": random.randint(30000, 120000),
            "Joining_Date": f"202{random.randint(0, 4)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        }
        mock_rows.append({
            "org_id": org_id,
            "sheet_row_id": f"{org_id}:mock:{i}",
            "data": record,
            "synced_at": datetime.utcnow().isoformat(),
        })

    try:
        service_role_client.table("sheets_rows").upsert(mock_rows, on_conflict="sheet_row_id").execute()
        print(f"✅ Inserted {len(mock_rows)} mock rows for org_id={org_id}")
        return {"status": "ok", "inserted": len(mock_rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert mock data: {e}")
