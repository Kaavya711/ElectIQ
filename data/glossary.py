"""
Election glossary data for ElectIQ.

Provides searchable term definitions scoped to each supported country.
Terms include the full name, a short abbreviation where applicable,
a plain-language definition, and a real-world usage example.

Structure:
    GLOSSARY[country_code] → list[GlossaryTerm]
"""

from typing import TypedDict


class GlossaryTerm(TypedDict):
    """A single glossary entry."""

    term: str       # Abbreviation or short name (e.g. "EVM")
    short: str      # Full expansion (e.g. "Electronic Voting Machine")
    definition: str
    example: str


GLOSSARY: dict[str, list[GlossaryTerm]] = {
    "IN": [
        {
            "term": "EVM",
            "short": "Electronic Voting Machine",
            "definition": (
                "A standalone electronic device used to record votes. "
                "It consists of a Control Unit and a Balloting Unit."
            ),
            "example": "In the 2024 Lok Sabha elections, over 5 million EVMs were deployed.",
        },
        {
            "term": "VVPAT",
            "short": "Voter Verifiable Paper Audit Trail",
            "definition": (
                "A machine attached to the EVM that prints a paper slip showing the symbol "
                "and candidate the voter chose, allowing them to verify their vote."
            ),
            "example": "The VVPAT slip is visible for 7 seconds before falling into a sealed drop box.",
        },
        {
            "term": "EPIC",
            "short": "Electors Photo Identity Card",
            "definition": "Commonly known as the Voter ID card, issued by the Election Commission of India.",
            "example": (
                "You should bring your EPIC to the polling booth, but other IDs are also "
                "accepted if you are on the roll."
            ),
        },
        {
            "term": "Model Code of Conduct",
            "short": "MCC",
            "definition": (
                "A set of guidelines issued by the Election Commission of India for the conduct "
                "of political parties and candidates during elections, covering speeches, polling "
                "day, polling booths, portfolios, manifestos, processions, and general conduct."
            ),
            "example": "The Model Code of Conduct comes into force immediately when the election schedule is announced.",
        },
        {
            "term": "Constituency",
            "short": "Electoral District",
            "definition": "A geographically defined area in which voters elect a representative to a legislative body.",
            "example": "India is divided into 543 parliamentary constituencies for Lok Sabha elections.",
        },
        {
            "term": "Returning Officer",
            "short": "RO",
            "definition": (
                "The statutory authority responsible for conducting the election in a constituency. "
                "They are typically district magistrates."
            ),
            "example": "The Returning Officer scrutinises nomination papers and officially declares the result.",
        },
        {
            "term": "Presiding Officer",
            "short": "PO",
            "definition": "The official in charge of a specific polling station on election day.",
            "example": "The Presiding Officer ensures the EVMs are functioning and polling is conducted fairly.",
        },
        {
            "term": "Form 6",
            "short": "Application for Registration",
            "definition": "The form used by eligible citizens to apply for inclusion of their name in the electoral roll.",
            "example": "If you just turned 18, fill out Form 6 online to get your Voter ID.",
        },
        {
            "term": "Form 8",
            "short": "Application for Correction",
            "definition": (
                "The form used to request corrections in the electoral roll, "
                "such as a change of address or name."
            ),
            "example": "If you move to a new city, submit Form 8 to transfer your registration.",
        },
        {
            "term": "Form 26",
            "short": "Candidate Affidavit",
            "definition": (
                "A sworn document filed by candidates detailing their assets, liabilities, "
                "educational qualifications, and criminal records (if any)."
            ),
            "example": "Voters can review a candidate's Form 26 on the ECI website to make an informed choice.",
        },
        {
            "term": "FPTP",
            "short": "First Past The Post",
            "definition": (
                "An electoral system where the candidate with the most votes in a constituency "
                "wins, even if they do not have an absolute majority."
            ),
            "example": "India and the UK use the FPTP system for their general elections.",
        },
    ],
    "US": [
        {
            "term": "Electoral College",
            "short": "EC",
            "definition": (
                "The group of presidential electors required by the Constitution to form every "
                "four years for the sole purpose of electing the president and vice president."
            ),
            "example": "A candidate needs 270 Electoral College votes to win the presidency.",
        },
    ],
    "GB": [
        {
            "term": "MP",
            "short": "Member of Parliament",
            "definition": "A person formally elected to the UK House of Commons.",
            "example": "There are 650 MPs in the UK Parliament.",
        },
    ],
    "AU": [
        {
            "term": "Preferential Voting",
            "short": "Ranked Voting",
            "definition": (
                "A system where voters rank candidates in order of preference. If no candidate "
                "gets an absolute majority, the candidate with the fewest votes is eliminated and "
                "their votes are redistributed according to the next preferences."
            ),
            "example": "Australia uses preferential voting for the House of Representatives.",
        },
    ],
    "DE": [
        {
            "term": "Bundestag",
            "short": "Federal Diet",
            "definition": "The national parliament of the Federal Republic of Germany.",
            "example": "The Bundestag elects the Chancellor and passes federal legislation.",
        },
    ],
}