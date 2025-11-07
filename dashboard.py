import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

# ==============================
# CONFIGURATION
# ==============================
API_URL = "http://127.0.0.1:8000"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsInJvbGUiOiJhdXRoZW50aWNhdGVkIiwib3JnX2lkIjoib3JnXzAwMSIsImV4cCI6MTc2MjQ0NzcwOSwiaWF0IjoxNzYyNDQ0MTA5LCJuYmYiOjE3NjI0NDQxMDl9.hlA372jFnTVkr_1lfHp7-JR_4udBFl8wyvdA-9oXAsQ"
ORG_ID = "org_001"
SPREADSHEET_ID = "1uFI5pW8EV2D02MKbdsH6NCUk2Qb1wB-i9iUC5aL0_jw"
SHEET_NAME = "Sheet1"

HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json",
}

# ==============================
# PAGE SETUP + STYLE
# ==============================
st.set_page_config(page_title="🤖 AI Agent Dashboard", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 10%, #1e293b 90%);
        color: white;
    }
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar-title {
        font-size: 26px;
        font-weight: 800;
        text-align: center;
        color: #38bdf8;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 15px;
        color: #94a3b8;
        font-weight: 700;
        margin-top: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .fancy-btn {
        display: block;
        text-align: center;
        background: rgba(56,189,248,0.08);
        color: #f1f5f9;
        border: 1px solid rgba(56,189,248,0.3);
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        padding: 10px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }
    .fancy-btn:hover {
        background: rgba(56,189,248,0.25);
        transform: translateY(-3px);
        box-shadow: 0 0 12px rgba(56,189,248,0.4);
    }
    .success-msg {
        background: rgba(34,197,94,0.15);
        color: #22c55e;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        padding: 6px;
        margin-top: 5px;
    }
    .stat-card {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }
    .big-font {
        font-size: 24px !important;
        font-weight: 600;
        color: #38bdf8;
    }
    .chat-box {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 15px;
        color: #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR CONTROLS
# ==============================
with st.sidebar:
    st.markdown("<div class='sidebar-title'>⚙️ Controls</div>", unsafe_allow_html=True)

    def safe_post(url, payload):
        try:
            res = requests.post(url, headers=HEADERS, json=payload)
            if res.status_code != 200:
                st.error(f"❌ {res.status_code}: {res.text}")
            else:
                return res.json()
        except Exception as e:
            st.error(f"Request failed: {e}")
        return None

    # --- Data Sync ---
    st.markdown("<div class='section-header'>📊 Data Sync</div>", unsafe_allow_html=True)
    if st.button("🔄 Sync Google Sheet"):
        with st.spinner("Syncing Google Sheet with Supabase..."):
            safe_post(f"{API_URL}/sync-sheet", {
                "spreadsheet_id": SPREADSHEET_ID,
                "sheet_name": SHEET_NAME,
                "org_id": ORG_ID,
            })
        st.markdown("<div class='success-msg'>✅ Sheet synced successfully!</div>", unsafe_allow_html=True)

    # --- AI Agent ---
    st.markdown("<div class='section-header'>🤖 AI Automation</div>", unsafe_allow_html=True)
    if st.button("🧠 Run AI Agent"):
        with st.spinner("Running AI automation..."):
            safe_post(f"{API_URL}/run-agent", {"org_id": ORG_ID})
        st.markdown("<div class='success-msg'>🤖 AI Agent executed successfully!</div>", unsafe_allow_html=True)

# --- Utility ---
    st.markdown("<div class='section-header'>🧩 Utilities</div>", unsafe_allow_html=True)
    if st.button("📋 Refresh Sheet Data"):
        with st.spinner("Refreshing data from Google Sheet & Supabase..."):
            try:
            # Step 1: Clear old cache
                if "latest_data" in st.session_state:
                    del st.session_state["latest_data"]

            # Step 2: Trigger backend sync (Google Sheet → Supabase)
                sync_res = requests.post(f"{API_URL}/sync-sheet", headers=HEADERS, json={
                    "spreadsheet_id": SPREADSHEET_ID,
                    "sheet_name": SHEET_NAME,
                    "org_id": ORG_ID
                })
                if sync_res.status_code != 200:
                    st.error(f"❌ Sync failed: {sync_res.text}")
                else:
                    # Step 3: Fetch new rows
                    rows_res = requests.get(f"{API_URL}/rows", headers=HEADERS)
                    if rows_res.status_code == 200:
                        st.session_state["latest_data"] = rows_res.json().get("data", [])
                        st.success("✅ Sheet & Supabase data refreshed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to fetch new rows: {rows_res.text}")
            except Exception as e:
                st.error(f"Refresh failed: {e}")

# ==============================
# MAIN DASHBOARD
# ==============================
st.title("🤖 AI Agent Dashboard")

try:
    # ✅ Load data from session cache if available
    if "latest_data" not in st.session_state:
        res = requests.get(f"{API_URL}/rows", headers=HEADERS)
        st.session_state["latest_data"] = res.json().get("data", [])

    data = st.session_state["latest_data"]
    df = pd.DataFrame(data)

    if not df.empty:
        if "data" in df.columns:
            expanded = pd.json_normalize(df["data"])
            df = pd.concat([df.drop(columns=["data"]), expanded], axis=1)

        df.columns = [col.strip().replace("data.", "") for col in df.columns]
        df = df.fillna("")

        if "Salary" in df.columns:
            df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce").fillna(0)

        if "Location" in df.columns:
            df["City"] = df["Location"]
        else:
            df["City"] = ""

        total_employees = len(df)
        avg_salary = df["Salary"].mean() if "Salary" in df else 0
        total_departments = df["Department"].nunique() if "Department" in df else 0
        top_city = (
            df["City"].mode()[0]
            if "City" in df and not df["City"].isna().all()
            else "No City Data"
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='stat-card'><div class='big-font'>{total_employees}</div>Employees</div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='stat-card'><div class='big-font'>₹{avg_salary:,.0f}</div>Average Salary</div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='stat-card'><div class='big-font'>{total_departments}</div>Departments</div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='stat-card'><div class='big-font'>{top_city}</div>Top City</div>", unsafe_allow_html=True)

        # st.markdown("### 📊 Data Overview")
        # st.dataframe(df, width='stretch', hide_index=True)
        st.markdown("### 📊 Data Overview")

        with st.expander("📋 View Synced Data (from Supabase)"):
            st.dataframe(df, width='stretch', hide_index=True)


        st.markdown("### 📈 Insights")
        if "Department" in df.columns and "Salary" in df.columns:
            chart1 = px.bar(
                df.groupby("Department")["Salary"].mean().reset_index(),
                x="Department", y="Salary",
                color="Department",
                title="Average Salary by Department"
            )
            st.plotly_chart(chart1, width='stretch')

        if "City" in df.columns:
            chart2 = px.histogram(df, x="City", title="Employee Distribution by City", color="City")
            st.plotly_chart(chart2, width='stretch')
    else:
        st.warning("⚠️ No rows found in Supabase table `sheets_rows`.")

except Exception as e:
    st.error(f"Error fetching data: {e}")

# ==============================
# AI AGENT QUERY
# ==============================
st.markdown("---")
st.markdown("## 💬 Ask the AI Agent")

prompt = st.text_area("Ask something about your data:", placeholder="e.g., What's the highest paid department?")
if st.button("Ask AI"):
    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                resp = requests.post(f"{API_URL}/agent-query", headers=HEADERS, json={"prompt": prompt})
                if resp.status_code == 200:
                    ans = resp.json().get("answer", "")
                    st.markdown(f"<div class='chat-box'>{ans}</div>", unsafe_allow_html=True)
                else:
                    st.error(f"❌ AI error {resp.status_code}: {resp.text}")
            except Exception as e:
                st.error(f"AI request failed: {e}")

# ==============================
# DEBUG SECTION
# ==============================
st.markdown("---")
with st.expander("🧩 Debug Info"):
    try:
        info = requests.get(f"{API_URL}/debug/env", headers=HEADERS).json()
        st.json(info)
    except Exception as e:
        st.write(f"Debug fetch failed: {e}")
