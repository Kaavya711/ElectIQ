"""
Role- and status-aware checklist data for ElectIQ.

Structure:
    CHECKLISTS[country_code][role][registration_status] → list[ChecklistItem]

Each ChecklistItem is a dict with:
    id       — unique string identifier
    text     — human-readable task description
    deadline — optional deadline hint string, or None
"""

from typing import TypedDict


class ChecklistItem(TypedDict):
    """A single actionable checklist task."""

    id: str
    text: str
    deadline: str | None


# ── India ─────────────────────────────────────────────────────────────────────
_IN_VOTER_REGISTERED: list[ChecklistItem] = [
    {"id": "v_r_1", "text": "Verify name at electoralsearch.eci.gov.in", "deadline": None},
    {"id": "v_r_2", "text": "Download the Voter Helpline app", "deadline": None},
    {"id": "v_r_3", "text": "Locate your polling booth", "deadline": "⏱ Before polling day"},
    {"id": "v_r_4", "text": "Read each candidate's Form 26 affidavit", "deadline": None},
    {"id": "v_r_5", "text": "Carry EPIC or alternate ID on polling day", "deadline": "⏱ Polling Day"},
    {"id": "v_r_6", "text": "Reach booth before closing time", "deadline": "⏱ Polling Day"},
    {"id": "v_r_7", "text": "Verify the VVPAT slip after voting", "deadline": "⏱ Polling Day"},
]

_IN_VOTER_NOT_REGISTERED: list[ChecklistItem] = [
    {"id": "v_nr_1", "text": "Submit Form 6 at voterportal.eci.gov.in", "deadline": "⏱ Before electoral roll cutoff"},
    {"id": "v_nr_2", "text": "Wait for enrollment confirmation", "deadline": None},
    {"id": "v_nr_3", "text": "Verify name after roll update", "deadline": None},
    {"id": "v_nr_4", "text": "Download the Voter Helpline app", "deadline": None},
    {"id": "v_nr_5", "text": "Locate your polling booth", "deadline": "⏱ Before polling day"},
    {"id": "v_nr_6", "text": "Carry ID on polling day", "deadline": "⏱ Polling Day"},
    {"id": "v_nr_7", "text": "Verify VVPAT slip after voting", "deadline": "⏱ Polling Day"},
]

_IN_VOTER_UNSURE: list[ChecklistItem] = [
    {"id": "v_u_1", "text": "Check enrollment at electoralsearch.eci.gov.in", "deadline": "⏱ ASAP"},
    {"id": "v_u_2", "text": "If not found, submit Form 6", "deadline": "⏱ Before cutoff"},
    {"id": "v_u_3", "text": "If found but details wrong, submit Form 8", "deadline": "⏱ Before cutoff"},
    {"id": "v_u_4", "text": "Locate your polling booth", "deadline": None},
    {"id": "v_u_5", "text": "Carry EPIC or ID to vote", "deadline": "⏱ Polling Day"},
]

_IN_CANDIDATE_REGISTERED: list[ChecklistItem] = [
    {"id": "c_r_1", "text": "Check Eligibility Criteria", "deadline": None},
    {"id": "c_r_2", "text": "File Nomination (Form 2B)", "deadline": "⏱ By Nomination Deadline"},
    {"id": "c_r_3", "text": "Submit Affidavit (Form 26)", "deadline": "⏱ With Nomination"},
    {"id": "c_r_4", "text": "Adhere to Model Code of Conduct", "deadline": "Continuous"},
    {"id": "c_r_5", "text": "Submit Election Expenses", "deadline": "⏱ Post Election"},
]

_IN_LEARNER_REGISTERED: list[ChecklistItem] = [
    {"id": "l_1", "text": "Understand the FPTP System", "deadline": None},
    {"id": "l_2", "text": "Learn about EVMs and VVPATs", "deadline": None},
    {"id": "l_3", "text": "Read the Model Code of Conduct", "deadline": None},
    {"id": "l_4", "text": "Follow the Election Timeline", "deadline": None},
]


def _empty_role() -> dict[str, list[ChecklistItem]]:
    """Return an empty role bucket with all three registration statuses."""
    return {"Registered": [], "Not Registered": [], "Unsure": []}


def _default_role(items: list[ChecklistItem]) -> dict[str, list[ChecklistItem]]:
    """
    Return a role bucket where all statuses share the same item list.

    Args:
        items: The list of checklist items to assign to every status.

    Returns:
        Dict mapping each registration status to ``items``.
    """
    return {"Registered": items, "Not Registered": items, "Unsure": items}


def _build_country_stub(
    voter_items: list[ChecklistItem],
) -> dict[str, dict[str, list[ChecklistItem]]]:
    """
    Build a minimal country checklist with Voter data and stub Candidate/Learner entries.

    Args:
        voter_items: Items to use for all Voter registration statuses.

    Returns:
        Country checklist dict with Voter, Candidate, and Learner keys.
    """
    _default_candidate: list[ChecklistItem] = [
        {"id": "c_default", "text": "Follow official guidelines for candidates.", "deadline": None}
    ]
    _default_learner: list[ChecklistItem] = [
        {"id": "l_default", "text": "Study the election process for this country.", "deadline": None}
    ]
    return {
        "Voter": _default_role(voter_items),
        "Candidate": _default_role(_default_candidate),
        "Learner": _default_role(_default_learner),
    }


# ── Checklist registry ────────────────────────────────────────────────────────
CHECKLISTS: dict[str, dict[str, dict[str, list[ChecklistItem]]]] = {
    "IN": {
        "Voter": {
            "Registered": _IN_VOTER_REGISTERED,
            "Not Registered": _IN_VOTER_NOT_REGISTERED,
            "Unsure": _IN_VOTER_UNSURE,
        },
        "Candidate": {
            "Registered": _IN_CANDIDATE_REGISTERED,
            "Not Registered": [],
            "Unsure": [],
        },
        "Learner": {
            "Registered": _IN_LEARNER_REGISTERED,
            "Not Registered": [],
            "Unsure": [],
        },
    },
    "US": _build_country_stub(
        voter_items=[
            {"id": "us_v_r_1", "text": "Check your voter registration status online.", "deadline": None},
            {"id": "us_v_r_2", "text": "Find your polling place.", "deadline": "⏱ Before Election Day"},
            {"id": "us_v_r_3", "text": "Bring required photo ID (varies by state).", "deadline": "⏱ Election Day"},
        ]
    ),
    "GB": _build_country_stub(
        voter_items=[
            {"id": "gb_v_r_1", "text": "Bring an accepted form of Photo ID.", "deadline": "⏱ Polling Day"},
            {"id": "gb_v_r_2", "text": "Find your polling station via gov.uk.", "deadline": None},
        ]
    ),
    "AU": _build_country_stub(
        voter_items=[
            {"id": "au_v_r_1", "text": "Vote — it is compulsory for enrolled citizens.", "deadline": "⏱ Polling Day"},
            {"id": "au_v_r_2", "text": "Find your polling place at aec.gov.au.", "deadline": "⏱ Before Polling Day"},
        ]
    ),
    "DE": _build_country_stub(
        voter_items=[
            {"id": "de_v_r_1", "text": "Receive your Wahlbenachrichtigung (polling card) by mail.", "deadline": "⏱ ~3 weeks before"},
            {"id": "de_v_r_2", "text": "Bring your ID and polling card on election day.", "deadline": "⏱ Election Day"},
        ]
    ),
}