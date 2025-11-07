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
