"""
Supported countries for ElectIQ.

Each entry maps an ISO 3166-1 alpha-2 country code to a dict containing:
    code  — the ISO code (string, 2 characters)
    name  — human-readable country name
    emoji — flag emoji for display in the UI
"""

from typing import TypedDict


class CountryInfo(TypedDict):
    """Type definition for a single country entry."""

    code: str
    name: str
    emoji: str


COUNTRIES: dict[str, CountryInfo] = {
    "IN": {"code": "IN", "name": "India", "emoji": "🇮🇳"},
    "US": {"code": "US", "name": "United States", "emoji": "🇺🇸"},
    "GB": {"code": "GB", "name": "United Kingdom", "emoji": "🇬🇧"},
    "AU": {"code": "AU", "name": "Australia", "emoji": "🇦🇺"},
    "DE": {"code": "DE", "name": "Germany", "emoji": "🇩🇪"},
}