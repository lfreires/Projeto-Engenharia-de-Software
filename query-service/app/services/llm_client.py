import os

from openai import OpenAI

from app.config import settings

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=settings.groq_api_key,
)

PRIMARY_MODEL = settings.primary_llm_model
FALLBACK_MODEL = settings.fallback_llm_model


def chat_completion(messages: list[dict], model: str = PRIMARY_MODEL) -> tuple[str, str]:
    """Call Groq LLM. Returns (answer, model_used).

    Falls back automatically to FALLBACK_MODEL if primary returns 429.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=1024,
        )
        return response.choices[0].message.content, model
    except Exception as e:
        if "429" in str(e) and model == PRIMARY_MODEL:
            return chat_completion(messages, model=FALLBACK_MODEL)
        raise
