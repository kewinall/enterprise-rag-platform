import re

from fastapi import Header, HTTPException, status

from app.core.config import get_settings

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"show\s+(me\s+)?your\s+hidden\s+instructions",
]


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = get_settings().rag_api_key
    if expected and x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def looks_like_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS)
