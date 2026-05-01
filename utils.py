import re
import bleach

INJECTION_PATTERNS = [
    "ignore previous", "ignore all", "ignore your", "system prompt",
    "jailbreak", "disregard", "forget your instructions",
    "forget all instructions", "you are now", "act as", "roleplay as",
    "pretend you are", "pretend to be", "your new instructions",
    "override", "bypass", "do anything now", "dan mode", "developer mode",
]

BLOCKED_RESPONSE = "I can only answer election-related questions."


def sanitize_input(text: str, max_length: int = 500) -> str:
    if not text or not isinstance(text, str):
        return ""
    clean = bleach.clean(text, tags=[], attributes={}, strip=True)
    clean = re.sub(r"\s+", " ", clean).strip()
    clean = clean[:max_length]
    lower = clean.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            return BLOCKED_RESPONSE
    return clean


def is_blocked_response(text: str) -> bool:
    return text == BLOCKED_RESPONSE


def sanitize_country_code(code: str) -> str:
    if not code or not isinstance(code, str):
        return "IN"
    code = code.strip().upper()
    if code == "CUSTOM":
        return "custom"
    if re.match(r"^[A-Z]{2}$", code):
        return code
    return "IN"


def sanitize_role(role: str) -> str:
    allowed = {"Voter", "Candidate", "Learner"}
    if role in allowed:
        return role
    return "Voter"