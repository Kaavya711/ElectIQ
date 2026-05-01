"""Checklist tests for ElectIQ — page rendering, state API, and data integrity."""

import json
import pytest
from app import app
from data.checklists import CHECKLISTS


@pytest.fixture
def client():
    """Create a Flask test client with rate limiting disabled."""
    app.config["TESTING"] = True
    app.config["RATELIMIT_ENABLED"] = False
    with app.test_client() as client:
        yield client


# ── Page rendering ────────────────────────────────────────────────────────────

def test_checklist_loads_for_voter(client):
    with client.session_transaction() as sess:
        sess["role"] = "Voter"
    response = client.get("/dashboard/IN/checklist")
    assert response.status_code == 200


def test_checklist_loads_for_candidate(client):
    with client.session_transaction() as sess:
        sess["role"] = "Candidate"
    response = client.get("/dashboard/IN/checklist")
    assert response.status_code == 200


def test_checklist_loads_for_learner(client):
    with client.session_transaction() as sess:
        sess["role"] = "Learner"
    response = client.get("/dashboard/IN/checklist")
    assert response.status_code == 200


def test_checklist_loads_without_role(client):
    """Defaults to Voter when no role is set in session."""
    response = client.get("/dashboard/IN/checklist")
    assert response.status_code == 200


def test_checklist_invalid_country(client):
    response = client.get("/dashboard/XYZ/checklist")
    assert response.status_code == 404


def test_checklist_all_supported_countries(client):
    for code in ("IN", "US", "GB", "AU", "DE"):
        response = client.get(f"/dashboard/{code}/checklist")
        assert response.status_code == 200, f"Failed for country {code}"


# ── State API ─────────────────────────────────────────────────────────────────

def test_checklist_state_post(client):
    response = client.post(
        "/api/checklist-state?country=IN&role=Voter",
        json={"task_1": True, "task_2": False},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data


def test_checklist_state_get(client):
    client.post("/api/checklist-state?country=IN&role=Voter", json={"task_1": True})
    response = client.get("/api/checklist-state?country=IN&role=Voter")
    assert response.status_code == 200


def test_checklist_state_persistence(client):
    client.post(
        "/api/checklist-state?country=IN&role=Voter",
        json={"task_1": True, "task_2": False},
    )
    response = client.get("/api/checklist-state?country=IN&role=Voter")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)


def test_checklist_state_post_returns_status_key(client):
    response = client.post(
        "/api/checklist-state?country=IN&role=Voter",
        json={"v_r_1": True},
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data


def test_checklist_state_get_returns_dict(client):
    response = client.get("/api/checklist-state?country=IN&role=Voter")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)


def test_checklist_us_voter(client):
    with client.session_transaction() as sess:
        sess["role"] = "Voter"
    response = client.get("/dashboard/US/checklist")
    assert response.status_code == 200


# ── Data integrity ────────────────────────────────────────────────────────────

def test_checklist_data_has_all_countries():
    for code in ("IN", "US", "GB", "AU", "DE"):
        assert code in CHECKLISTS, f"Missing country: {code}"


def test_checklist_data_has_all_roles():
    for code, country_data in CHECKLISTS.items():
        for role in ("Voter", "Candidate", "Learner"):
            assert role in country_data, f"Missing role {role} for {code}"


def test_checklist_data_has_all_statuses():
    for code, country_data in CHECKLISTS.items():
        for role, role_data in country_data.items():
            for status in ("Registered", "Not Registered", "Unsure"):
                assert status in role_data, (
                    f"Missing status '{status}' for {code}/{role}"
                )


def test_checklist_items_have_required_fields():
    for code, country_data in CHECKLISTS.items():
        for role, role_data in country_data.items():
            for status, items in role_data.items():
                for item in items:
                    assert "id" in item, f"Missing 'id' in {code}/{role}/{status}"
                    assert "text" in item, f"Missing 'text' in {code}/{role}/{status}"
                    assert "deadline" in item, f"Missing 'deadline' in {code}/{role}/{status}"


def test_checklist_india_voter_registered_not_empty():
    items = CHECKLISTS["IN"]["Voter"]["Registered"]
    assert len(items) >= 5, "India registered voter checklist should have at least 5 items"


def test_checklist_item_ids_are_unique():
    seen_ids: set[str] = set()
    for code, country_data in CHECKLISTS.items():
        for role, role_data in country_data.items():
            for status, items in role_data.items():
                for item in items:
                    item_id = item["id"]
                    assert item_id not in seen_ids, f"Duplicate checklist item id: {item_id}"
                    seen_ids.add(item_id)