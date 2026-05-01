"""
Pre-loaded election myth/fact pairs for ElectIQ's Myth Buster feature.

Each entry provides a static verdict so the page is functional even when
the Gemini API is unavailable. The AI endpoint supplements these with
real-time fact-checking for user-submitted claims.

Structure:
    MYTHS[country_code] → list[MythEntry]
"""

from typing import TypedDict


class MythEntry(TypedDict):
    """A single pre-loaded myth with its verdict and explanation."""

    myth: str
    verdict: str        # One of: "TRUE", "FALSE", "PARTIAL"
    explanation: str
    source: str


MYTHS: dict[str, list[MythEntry]] = {
    "IN": [
        {
            "myth": "You need Aadhaar to vote",
            "verdict": "FALSE",
            "explanation": (
                "Aadhaar is not mandatory for voting. You can use your EPIC (Voter ID) "
                "or any of the 11 alternative photo identity documents approved by the ECI, "
                "such as a Passport, PAN card, or Driving License."
            ),
            "source": "https://eci.gov.in",
        },
        {
            "myth": "NRIs cannot vote in Indian elections",
            "verdict": "PARTIAL",
            "explanation": (
                "Non-Resident Indians (NRIs) who have not acquired citizenship of any other "
                "country are eligible to be registered as voters. However, they must cast their "
                "vote in person at their designated polling station in India; postal ballots or "
                "online voting are not yet available for them."
            ),
            "source": "https://eci.gov.in",
        },
        {
            "myth": "EVMs can be easily hacked",
            "verdict": "FALSE",
            "explanation": (
                "Indian Electronic Voting Machines (EVMs) are standalone, non-networked devices. "
                "They cannot be connected to the internet, Bluetooth, or any wireless network, "
                "making remote hacking technically impossible."
            ),
            "source": "https://eci.gov.in",
        },
        {
            "myth": "You can vote without Voter ID if your name is on the roll",
            "verdict": "TRUE",
            "explanation": (
                "If your name is on the electoral roll, you can vote even without your Voter ID "
                "card, provided you show an alternative approved photo ID (like a Passport, PAN "
                "card, or Aadhaar) to establish your identity."
            ),
            "source": "https://eci.gov.in",
        },
        {
            "myth": "Candidates must be graduates to contest",
            "verdict": "FALSE",
            "explanation": (
                "There are no educational qualifications required by the Constitution of India "
                "to contest in general elections for the Lok Sabha or Legislative Assemblies."
            ),
            "source": "https://eci.gov.in",
        },
    ],
    "US": [
        {
            "myth": "You can vote online in federal elections",
            "verdict": "FALSE",
            "explanation": (
                "Currently, no state allows general online voting for federal elections due to "
                "security concerns. Some states allow online return for military/overseas voters, "
                "but traditional voting is in-person or by mail."
            ),
            "source": "https://vote.gov",
        },
    ],
    "GB": [
        {
            "myth": "You can't vote if you don't have a polling card",
            "verdict": "FALSE",
            "explanation": (
                "You do not need your polling card to vote, but you do need to be on the "
                "electoral register and, importantly, you must bring an accepted form of photo ID."
            ),
            "source": "https://electoralcommission.org.uk",
        },
    ],
    "AU": [
        {
            "myth": "Voting is optional",
            "verdict": "FALSE",
            "explanation": (
                "Voting in Australian federal elections is compulsory for all eligible citizens "
                "aged 18 and over. Failure to vote without a valid reason may result in a fine."
            ),
            "source": "https://aec.gov.au",
        },
    ],
    "DE": [
        {
            "myth": "The Chancellor is elected directly by the people",
            "verdict": "FALSE",
            "explanation": (
                "The Chancellor is elected by the members of the Bundestag (Parliament), not "
                "directly by the citizens. Citizens vote for parties and local representatives."
            ),
            "source": "https://bundeswahlleiterin.de",
        },
    ],
}