"""
Input sanitization utilities for ElectIQ.

All user-supplied text must pass through ``sanitize_input`` before being
forwarded to the Gemini API or written to the database. Country codes and
roles are validated against explicit allowlists.
"""

import re

import bleach

# ── Prompt-injection patterns ─────────────────────────────────────────────────
_INJECTION_PATTERNS: list[str] = [
    "ignore previous",
    "ignore all",
    "ignore your",
    "system prompt",
    "jailbreak",
    "disregard",
    "forget your instructions",
    "forget all instructions",
    "you are now",
    "act as",
    "roleplay as",
    "pretend you are",
    "pretend to be",
    "your new instructions",
    "override",
    "bypass",
    "do anything now",
    "dan mode",
    "developer mode",
]

BLOCKED_RESPONSE: str = "I can only answer election-related questions."

_ALLOWED_ROLES: frozenset[str] = frozenset({"Voter", "Candidate", "Learner"})
_DEFAULT_COUNTRY: str = "IN"
_COUNTRY_CODE_RE = re.compile(r"^[A-Z]{2}$")


def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize a free-text user input for safe use in AI prompts and DB writes.

    Steps:
        1. Strip all HTML tags via bleach.
        2. Collapse whitespace.
        3. Truncate to ``max_length`` characters.
        4. Reject strings that contain known prompt-injection patterns.

    Args:
        text: Raw user-supplied string.
        max_length: Maximum allowed character length (default 500).

    Returns:
        Cleaned string, or ``BLOCKED_RESPONSE`` if injection is detected.
    """
    if not text or not isinstance(text, str):
        return ""
    clean: str = bleach.clean(text, tags=[], attributes={}, strip=True)
    clean = re.sub(r"\s+", " ", clean).strip()
    clean = clean[:max_length]
    lower: str = clean.lower()
    for pattern in _INJECTION_PATTERNS:
        if pattern in lower:
            return BLOCKED_RESPONSE
    return clean


def is_blocked_response(text: str) -> bool:
    """
    Return True if ``text`` is the standard blocked-response sentinel.

    Args:
        text: String to test.

    Returns:
        True when ``text`` equals ``BLOCKED_RESPONSE``.
    """
    return text == BLOCKED_RESPONSE


def sanitize_country_code(code: str) -> str:
    """
    Validate and normalise an ISO 3166-1 alpha-2 country code.

    ``"custom"`` (case-insensitive) is passed through unchanged.
    Any other value that is not exactly two ASCII letters defaults to ``"IN"``.

    Args:
        code: Raw country code string from user input.

    Returns:
        Upper-cased two-letter code, ``"custom"``, or ``"IN"`` as fallback.
    """
    if not code or not isinstance(code, str):
        return _DEFAULT_COUNTRY
    normalised: str = code.strip().upper()
    if normalised == "CUSTOM":
        return "custom"
    if _COUNTRY_CODE_RE.match(normalised):
        return normalised
    return _DEFAULT_COUNTRY


def sanitize_role(role: str) -> str:
    """
    Validate a user role string against the allowed roles allowlist.

    Args:
        role: Raw role string from user input.

    Returns:
        The validated role, or ``"Voter"`` as the default fallback.
    """
    if role in _ALLOWED_ROLES:
        return role
    return "Voter"