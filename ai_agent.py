# # ai_agent.py
# import json
# from typing import Optional, List, Dict
# from openai import AsyncOpenAI, OpenAIError

# # ==============================
# # ✅ Local API Key Loader (no .env)
# # ==============================
# def load_local_key() -> Optional[str]:
#     """
#     Load OpenAI API key directly from config_local.json.
#     Returns None if file or key not found.
#     """
#     try:
#         with open("config_local.json", "r") as f:
#             data = json.load(f)
#             return data.get("OPENAI_API_KEY")
#     except FileNotFoundError:
#         print("⚠️ config_local.json not found — running in MOCK mode.")
#         return None
#     except Exception as e:
#         print(f"⚠️ Failed to read local key: {e}")
#         return None

# # Load key locally
# OPENAI_API_KEY = load_local_key()

# if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
#     print("⚠️ No valid OpenAI API key found. Running in MOCK MODE.")
#     client = None
# else:
#     client = AsyncOpenAI(api_key=OPENAI_API_KEY)
#     print("✅ OpenAI client initialized successfully.")


# # ==============================
# # 🧠 Core Function
# # ==============================
# async def ask_openai(
#     prompt: str,
#     model: str = "gpt-4o-mini",
#     max_tokens: int = 512,
#     system_prompt: Optional[str] = None,
# ) -> str:
#     """
#     Sends a prompt to OpenAI API.
#     Falls back to mock response if key missing or invalid.
#     """

#     if client is None:
#         print("🤖 [MOCK MODE] Responding without OpenAI API...")
#         return f"(mocked) Response to your prompt: '{prompt[:60]}...'"

#     try:
#         messages: List[Dict[str, str]] = []
#         if system_prompt:
#             messages.append({"role": "system", "content": system_prompt})
#         messages.append({"role": "user", "content": prompt})

#         response = await client.chat.completions.create(
#             model=model,
#             messages=messages,
#             max_tokens=max_tokens,
#             temperature=0.2,
#         )

#         return response.choices[0].message.content.strip()

#     except OpenAIError as e:
#         err_msg = str(e)
#         print(f"⚠️ OpenAI API error: {err_msg}")
#         if "invalid_api_key" in err_msg or "insufficient_quota" in err_msg:
#             print("🤖 Switching to MOCK MODE due to API error...")
#             return f"(mocked fallback) Response to: '{prompt[:60]}...'"
#         raise


# ai_agent.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# ===============================
# Load environment variables
# ===============================
load_dotenv()

# --- Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-4o"  # OpenRouter GPT-4o model (multimodal + fast)

if not OPENROUTER_API_KEY:
    raise ValueError("❌ Missing OPENROUTER_API_KEY in .env file!")

# --- Initialize OpenRouter client ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# ===============================
# Main function used by your app
# ===============================
async def ask_openai(
    prompt: str,
    system_prompt: str = "You are a helpful AI data analyst that provides concise insights.",
    temperature: float = 0.3,
    max_tokens: int = 512
):
    """
    Ask OpenRouter's GPT-4o model a question and get a response.
    Automatically handles errors and returns fallback text if API fails.
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                "HTTP-Referer": "http://localhost:8501",  # optional: for OpenRouter analytics
                "X-Title": "AI-Agent-Dashboard",
            },
        )

        # ✅ Return the model’s answer
        return completion.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ OpenRouter API error: {e}")
        return f"(mocked fallback) Response to: '{prompt[:50]}...'"

# ===============================
# Standalone test (optional)
# ===============================
if __name__ == "__main__":
    import asyncio

    async def test():
        response = await ask_openai("Give me 3 creative startup ideas using AI.")
        print("\n🧠 AI Response:\n", response)

    asyncio.run(test())
