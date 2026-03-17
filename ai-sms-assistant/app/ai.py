import logging
import os

import httpx

logger = logging.getLogger(__name__)

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4.1-mini")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1/chat/completions")

SYSTEM_PROMPT = (
    "You are an SMS assistant. Keep replies short and practical (max 300 characters). "
    "If the user asks about weather, suggest: 'weather 3 days <city>'. "
    "If uncertain, ask one short clarifying question."
)


async def _openai_chat(prompt: str) -> str:
    if not AI_API_KEY:
        return "Server missing AI_API_KEY. Ask admin to configure it."

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 200,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(AI_BASE_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        return (data["choices"][0]["message"]["content"] or "").strip()


async def handle_ai(user_text: str, from_number: str | None = None) -> str:
    if AI_PROVIDER == "openai":
        return await _openai_chat(user_text)
    logger.warning("Unsupported AI_PROVIDER=%r", AI_PROVIDER)
    return "AI_PROVIDER not supported. Set AI_PROVIDER=openai in .env."
