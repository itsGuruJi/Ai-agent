# 🤖 AI Agent Dashboard

A **full-stack AI automation system** built using **FastAPI**, **Supabase**, and **Streamlit**, integrated with **Google Sheets** and **OpenAI / OpenRouter** to deliver real-time insights, data synchronization, and AI-driven analysis.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🚀 Overview

The **AI Agent Dashboard** connects directly to a Google Sheet, syncs all data into Supabase, and provides:
- Live analytics through a modern Streamlit dashboard  
- AI-powered query responses (“Which department has the highest salary?”)  
- Real-time organization-level data insights  
- Secure JWT authentication for role-based access  

This project demonstrates how to unify **data engineering + AI + web visualization** into one seamless pipeline.

---

## 🧱 Tech Stack

| Layer | Technology | Purpose |
|-------|-------------|----------|
| 🧩 Backend | [FastAPI](https://fastapi.tiangolo.com/) | Handles API routes, AI agent queries, and sheet synchronization |
| 🗄️ Database | [Supabase](https://supabase.com/) | Stores all sheet data (PostgreSQL + REST + RLS) |
| 🧠 AI | [OpenAI](https://platform.openai.com/) / [OpenRouter](https://openrouter.ai/) | Provides generative reasoning and data insights |
| 📊 Frontend | [Streamlit](https://streamlit.io/) | Displays analytics, metrics, and interactive AI chat |
| 📗 Sheets | [Google Sheets API](https://developers.google.com/sheets/api) | Data ingestion & syncing |
| 🔐 Auth | JWT Tokens | Org-based secure API access |

---

## ⚙️ Features

✅ **Google Sheets → Supabase Sync** (via FastAPI endpoint)  
✅ **AI-powered insights** using GPT models  
✅ **Interactive Streamlit dashboard** with charts (Plotly)  
✅ **Organization-based data filtering (org_id)**  
✅ **JWT-secured backend APIs**  
✅ **Real-time analytics** on employees, salaries, and departments  
✅ **Modular & deployable architecture**

---

## 🧭 System Architecture

```text
Google Sheet  --->  FastAPI (/sync-sheet)
                      |
                      ↓
                  Supabase DB
                      |
         ┌────────────┴────────────┐
         ↓                         ↓
 Streamlit Dashboard          AI Agent (GPT)


Ai-agent/
│
├── main.py                # FastAPI backend
├── ai_agent.py            # Handles GPT/AI queries
├── dashboard.py           # Streamlit dashboard UI
├── supabase_client.py     # Supabase integration (service & RLS clients)
├── google_sync.py         # Google Sheets → Supabase sync logic
├── generate_jwt.py        # JWT token generator
├── .env.example           # Example environment configuration
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT license
└── README.md              # Project documentation (this file)


🧩 Setup Instructions
1️⃣ Clone this repo
git clone https://github.com/itsGuruJi/Ai-agent.git
cd Ai-agent

2️⃣ Create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # (for Windows)
# OR
source venv/bin/activate # (for macOS/Linux)

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure environment variables

Copy the example file:

cp .env.example .env


Then open .env and fill in your actual credentials:

OPENAI_API_KEY=your_openai_or_openrouter_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key
SUPABASE_ANON_KEY=your_anon_key
JWT_SECRET=your_jwt_secret

🧠 Running the Project
▶️ Start FastAPI backend
uvicorn main:app --reload


Backend runs on → http://127.0.0.1:8000

▶️ Start Streamlit dashboard
streamlit run dashboard.py


Dashboard opens on → http://localhost:8501

📊 Dashboard Features

Sync Google Sheets → imports fresh data into Supabase

Run AI Agent → auto-analyze your org’s data

View Metrics → Employees, Departments, Avg Salary, Top City

Ask AI → Query insights from your dataset in plain English

Plotly Charts → Interactive visual analytics

🧠 Example AI Prompts
"What is the highest-paid department?"
"Which city has the most employees?"
"What’s the average salary per department?"


The system uses GPT reasoning to answer from Supabase data.
