CHECKLISTS = {
    "IN": {
        "Voter": {
            "Registered": [
                {"id": "v_r_1", "text": "Verify name at electoralsearch.eci.gov.in", "deadline": None},
                {"id": "v_r_2", "text": "Download the Voter Helpline app", "deadline": None},
                {"id": "v_r_3", "text": "Locate your polling booth", "deadline": "⏱ Before polling day"},
                {"id": "v_r_4", "text": "Read each candidate's Form 26 affidavit", "deadline": None},
                {"id": "v_r_5", "text": "Carry EPIC or alternate ID on polling day", "deadline": "⏱ Polling Day"},
                {"id": "v_r_6", "text": "Reach booth before closing time", "deadline": "⏱ Polling Day"},
                {"id": "v_r_7", "text": "Verify the VVPAT slip after voting", "deadline": "⏱ Polling Day"}
            ],
            "Not Registered": [
                {"id": "v_nr_1", "text": "Submit Form 6 at voterportal.eci.gov.in", "deadline": "⏱ Before electoral roll cutoff"},
                {"id": "v_nr_2", "text": "Wait for enrollment confirmation", "deadline": None},
                {"id": "v_nr_3", "text": "Verify name after roll update", "deadline": None},
                {"id": "v_nr_4", "text": "Download the Voter Helpline app", "deadline": None},
                {"id": "v_nr_5", "text": "Locate your polling booth", "deadline": "⏱ Before polling day"},
                {"id": "v_nr_6", "text": "Carry ID on polling day", "deadline": "⏱ Polling Day"},
                {"id": "v_nr_7", "text": "Verify VVPAT slip after voting", "deadline": "⏱ Polling Day"}
            ],
            "Unsure": [
                {"id": "v_u_1", "text": "Check enrollment at electoralsearch.eci.gov.in", "deadline": "⏱ ASAP"},
                {"id": "v_u_2", "text": "If not found, submit Form 6", "deadline": "⏱ Before cutoff"},
                {"id": "v_u_3", "text": "If found but details wrong, submit Form 8", "deadline": "⏱ Before cutoff"},
                {"id": "v_u_4", "text": "Locate your polling booth", "deadline": None},
                {"id": "v_u_5", "text": "Carry EPIC or ID to vote", "deadline": "⏱ Polling Day"}
            ]
        },
        "Candidate": {
             "Registered": [
                {"id": "c_r_1", "text": "Check Eligibility Criteria", "deadline": None},
                {"id": "c_r_2", "text": "File Nomination (Form 2B)", "deadline": "⏱ By Nomination Deadline"},
                {"id": "c_r_3", "text": "Submit Affidavit (Form 26)", "deadline": "⏱ With Nomination"},
                {"id": "c_r_4", "text": "Adhere to Model Code of Conduct", "deadline": "Continuous"},
                {"id": "c_r_5", "text": "Submit Election Expenses", "deadline": "⏱ Post Election"}
             ],
             "Not Registered": [],
             "Unsure": []
        },
        "Learner": {
            "Registered": [
                {"id": "l_1", "text": "Understand the FPTP System", "deadline": None},
                {"id": "l_2", "text": "Learn about EVMs and VVPATs", "deadline": None},
                {"id": "l_3", "text": "Read the Model Code of Conduct", "deadline": None},
                {"id": "l_4", "text": "Follow the Election Timeline", "deadline": None}
            ],
            "Not Registered": [],
            "Unsure": []
        }
    },
    "US": {
         "Voter": {
            "Registered": [
                {"id": "us_v_r_1", "text": "Check registration status", "deadline": None},
                {"id": "us_v_r_2", "text": "Find polling place", "deadline": "⏱ Before Election Day"},
                {"id": "us_v_r_3", "text": "Bring required ID (varies by state)", "deadline": "⏱ Election Day"}
            ],
            "Not Registered": [],
            "Unsure": []
         },
         "Candidate": { "Registered": [], "Not Registered": [], "Unsure": []},
         "Learner": { "Registered": [], "Not Registered": [], "Unsure": []}
    },
    "GB": {
         "Voter": {
            "Registered": [
                 {"id": "gb_v_r_1", "text": "Bring Photo ID", "deadline": "⏱ Polling Day"},
                 {"id": "gb_v_r_2", "text": "Find Polling Station", "deadline": None}
            ],
            "Not Registered": [],
            "Unsure": []
         },
         "Candidate": { "Registered": [], "Not Registered": [], "Unsure": []},
         "Learner": { "Registered": [], "Not Registered": [], "Unsure": []}
    },
    "AU": {
         "Voter": {
            "Registered": [
                 {"id": "au_v_r_1", "text": "Vote! (It's compulsory)", "deadline": "⏱ Polling Day"}
            ],
            "Not Registered": [],
            "Unsure": []
         },
         "Candidate": { "Registered": [], "Not Registered": [], "Unsure": []},
         "Learner": { "Registered": [], "Not Registered": [], "Unsure": []}
    },
    "DE": {
         "Voter": {
            "Registered": [
                 {"id": "de_v_r_1", "text": "Receive polling card by mail", "deadline": "⏱ ~3 weeks before"},
                 {"id": "de_v_r_2", "text": "Bring ID and polling card", "deadline": "⏱ Election Day"}
            ],
            "Not Registered": [],
            "Unsure": []
         },
         "Candidate": { "Registered": [], "Not Registered": [], "Unsure": []},
         "Learner": { "Registered": [], "Not Registered": [], "Unsure": []}
    }
}
# Defaulting missing keys for simplification
for country in ["US", "GB", "AU", "DE"]:
    if "Not Registered" not in CHECKLISTS[country]["Voter"]:
        CHECKLISTS[country]["Voter"]["Not Registered"] = CHECKLISTS[country]["Voter"]["Registered"]
    if "Unsure" not in CHECKLISTS[country]["Voter"]:
        CHECKLISTS[country]["Voter"]["Unsure"] = CHECKLISTS[country]["Voter"]["Registered"]
    if "Registered" not in CHECKLISTS[country]["Candidate"] or not CHECKLISTS[country]["Candidate"]["Registered"]:
        CHECKLISTS[country]["Candidate"]["Registered"] = [{"id": "c_default", "text": "Follow official guidelines", "deadline": None}]
        CHECKLISTS[country]["Candidate"]["Not Registered"] = CHECKLISTS[country]["Candidate"]["Registered"]
        CHECKLISTS[country]["Candidate"]["Unsure"] = CHECKLISTS[country]["Candidate"]["Registered"]
    if "Registered" not in CHECKLISTS[country]["Learner"] or not CHECKLISTS[country]["Learner"]["Registered"]:
        CHECKLISTS[country]["Learner"]["Registered"] = [{"id": "l_default", "text": "Study the process", "deadline": None}]
        CHECKLISTS[country]["Learner"]["Not Registered"] = CHECKLISTS[country]["Learner"]["Registered"]
        CHECKLISTS[country]["Learner"]["Unsure"] = CHECKLISTS[country]["Learner"]["Registered"]
