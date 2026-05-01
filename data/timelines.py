"""
Election timeline data for ElectIQ.

Each country has an ordered list of timeline events. Every event includes
role-specific notes so the UI can surface relevant information for Voters,
Candidates, and Learners at each stage of the election process.

Structure:
    TIMELINES[country_code] → list[TimelineEvent]
"""

from typing import TypedDict


class TimelineEvent(TypedDict):
    """A single milestone in an election timeline."""

    day: str            # Relative day label (e.g. "Day 0", "Day ~45")
    title: str          # Short event title
    description: str    # Plain-language description of the milestone
    duration: str | None  # Duration string or None for single-day events
    voter_note: str     # Role-specific guidance for Voters
    candidate_note: str  # Role-specific guidance for Candidates
    learner_note: str   # Role-specific context for Learners


TIMELINES: dict[str, list[TimelineEvent]] = {
    "IN": [
        {
            "day": "Day 0",
            "title": "ECI Announces Schedule",
            "description": "The Election Commission announces poll dates at a press conference.",
            "duration": None,
            "voter_note": "Mark your calendar — verify your name on the electoral roll right away.",
            "candidate_note": "Begin assembling nomination documents and affidavits.",
            "learner_note": "The Model Code of Conduct takes effect immediately after announcement.",
        },
        {
            "day": "Day 0",
            "title": "Model Code of Conduct Begins",
            "description": "Guidelines for political parties and candidates come into force.",
            "duration": "Continuous",
            "voter_note": "Report any MCC violations you see using the cVIGIL app.",
            "candidate_note": "Ensure no government resources are used for campaigning.",
            "learner_note": "The MCC ensures a level playing field for all political parties.",
        },
        {
            "day": "Day ~14",
            "title": "Gazette Notification",
            "description": "Formal notification of the election is published.",
            "duration": None,
            "voter_note": "The window for filing nominations officially opens.",
            "candidate_note": "You can now officially file your nomination papers.",
            "learner_note": "This is the legal start of the election process.",
        },
        {
            "day": "Day ~21",
            "title": "Last Date for Nominations",
            "description": "Final day for candidates to submit their nomination papers.",
            "duration": None,
            "voter_note": "You will soon know the final list of candidates in your constituency.",
            "candidate_note": "Ensure all forms, including Form 26 (Affidavit), are submitted by 3 PM.",
            "learner_note": "Candidates must disclose their assets, liabilities, and criminal records.",
        },
        {
            "day": "Day ~24",
            "title": "Scrutiny of Nominations",
            "description": "Returning Officers verify the submitted nomination papers.",
            "duration": None,
            "voter_note": "Invalid nominations will be rejected at this stage.",
            "candidate_note": "Be present or send a representative to answer any queries.",
            "learner_note": "This step ensures all candidates meet constitutional requirements.",
        },
        {
            "day": "Day ~26",
            "title": "Last Date to Withdraw",
            "description": "Candidates can withdraw their nominations by this date.",
            "duration": None,
            "voter_note": "The final list of contesting candidates is published after this.",
            "candidate_note": "Submit a formal withdrawal notice if you decide not to contest.",
            "learner_note": "The final ballot paper layout is decided after withdrawals.",
        },
        {
            "day": "Day ~45",
            "title": "Polling Day",
            "description": "Voters cast their ballots at designated polling booths.",
            "duration": "1 Day",
            "voter_note": "Bring your EPIC or approved ID. Reach the booth before closing time.",
            "candidate_note": "Do not campaign within 100 metres of the polling station.",
            "learner_note": "Voting is conducted using Electronic Voting Machines (EVMs).",
        },
        {
            "day": "Day ~47",
            "title": "Counting Day",
            "description": "EVMs are unsealed and votes are counted at counting centres.",
            "duration": "1 Day",
            "voter_note": "Follow the ECI results portal for live constituency updates.",
            "candidate_note": "Assign counting agents to monitor the process at each table.",
            "learner_note": "Results are declared constituency by constituency as counting progresses.",
        },
        {
            "day": "Day ~48",
            "title": "Results Declared",
            "description": "Final results are officially published by the ECI.",
            "duration": None,
            "voter_note": "Your new representative is officially elected.",
            "candidate_note": "The winning candidate receives a certificate of election.",
            "learner_note": "The party or coalition with a majority forms the government.",
        },
    ],
    "US": [
        {
            "day": "Months Prior",
            "title": "Primary Elections",
            "description": "Parties select their nominees for the general election.",
            "duration": "Varies",
            "voter_note": "Register for your party's primary or caucus in your state.",
            "candidate_note": "Campaign heavily within your party to secure the nomination.",
            "learner_note": "Primaries and caucuses vary significantly by state.",
        },
        {
            "day": "Early Nov",
            "title": "Election Day",
            "description": "General election day for federal and state offices.",
            "duration": "1 Day",
            "voter_note": "Vote at your local precinct or submit your mail-in ballot on time.",
            "candidate_note": "Final push for voter turnout in key precincts.",
            "learner_note": "Held on the Tuesday following the first Monday in November.",
        },
    ],
    "GB": [
        {
            "day": "Day 0",
            "title": "Parliament Dissolved",
            "description": "The King dissolves Parliament on the advice of the Prime Minister.",
            "duration": None,
            "voter_note": "The election campaign officially begins.",
            "candidate_note": "You are no longer an MP; you are now a parliamentary candidate.",
            "learner_note": "Writs of Election are issued for all 650 constituencies.",
        },
        {
            "day": "Day 25",
            "title": "Polling Day",
            "description": "Voters cast their ballots at polling stations across the UK.",
            "duration": "1 Day",
            "voter_note": "Polling stations are open from 7 AM to 10 PM. Bring photo ID.",
            "candidate_note": "Get Out The Vote (GOTV) operations are in full swing.",
            "learner_note": "The UK uses the First Past The Post (FPTP) system.",
        },
    ],
    "AU": [
        {
            "day": "Day 0",
            "title": "Issue of Writ",
            "description": "The Governor-General issues writs for the election.",
            "duration": None,
            "voter_note": "Ensure your enrollment details are up to date immediately.",
            "candidate_note": "Prepare nomination paperwork.",
            "learner_note": "Australian federal elections must be held on a Saturday.",
        },
        {
            "day": "Day ~33",
            "title": "Polling Day",
            "description": "Voting takes place across Australia.",
            "duration": "1 Day",
            "voter_note": "Voting is compulsory in Australia — non-voters may be fined.",
            "candidate_note": "Hand out how-to-vote cards outside polling booths.",
            "learner_note": "Australia uses preferential (ranked-choice) voting.",
        },
    ],
    "DE": [
        {
            "day": "Months Prior",
            "title": "Candidate Selection",
            "description": "Parties select their list and direct candidates.",
            "duration": "Varies",
            "voter_note": "Review party programs and manifestos ahead of the campaign.",
            "candidate_note": "Secure your position on the state list or win the direct mandate.",
            "learner_note": "Germany uses a mixed-member proportional representation system.",
        },
        {
            "day": "Sunday",
            "title": "Election Day",
            "description": "Bundestagswahl — voting takes place across Germany.",
            "duration": "1 Day",
            "voter_note": "You have two votes: one for a person, one for a party.",
            "candidate_note": "Await the 6 PM exit polls for early indications.",
            "learner_note": "The second vote (Zweitstimme) determines the overall balance in the Bundestag.",
        },
    ],
}