"""Route smoke tests for ElectIQ — landing page, dashboard, country selection, role setting, and all feature pages."""

import pytest
from app import app


@pytest.fixture
def client():
    """Create a Flask test client with rate limiting disabled."""
    app.config["TESTING"] = True
    app.config["RATELIMIT_ENABLED"] = False
    with app.test_client() as client:
        yield client


# ── Landing page ──────────────────────────────────────────────────────────────

def test_landing_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Understand Elections." in response.data
    assert b"Select your country" in response.data


def test_landing_page_content_type(client):
    response = client.get("/")
    assert "text/html" in response.content_type


# ── Dashboard ─────────────────────────────────────────────────────────────────

def test_dashboard_india_loads(client):
    response = client.get("/dashboard/IN")
    assert response.status_code == 200
    assert b"India" in response.data


def test_dashboard_us_loads(client):
    response = client.get("/dashboard/US")
    assert response.status_code == 200
    assert b"United States" in response.data


def test_dashboard_gb_loads(client):
    response = client.get("/dashboard/GB")
    assert response.status_code == 200
    assert b"United Kingdom" in response.data


def test_dashboard_au_loads(client):
    response = client.get("/dashboard/AU")
    assert response.status_code == 200
    assert b"Australia" in response.data


def test_dashboard_de_loads(client):
    response = client.get("/dashboard/DE")
    assert response.status_code == 200
    assert b"Germany" in response.data


def test_invalid_country_returns_404(client):
    response = client.get("/dashboard/XYZ")
    assert response.status_code == 404


def test_empty_country_returns_404(client):
    response = client.get("/dashboard/")
    assert response.status_code == 404


def test_lowercase_country_returns_404(client):
    """Country codes are case-sensitive; lowercase should 404."""
    response = client.get("/dashboard/in")
    assert response.status_code == 404


# ── Country selection ─────────────────────────────────────────────────────────

def test_set_country_redirects_known(client):
    response = client.post("/set-country", data={"country_code": "US"})
    assert response.status_code == 302
    assert "/dashboard/US" in response.headers["Location"]


def test_set_country_redirects_custom(client):
    response = client.post("/set-country", data={"country_code": "custom", "custom_country": "Narnia"})
    assert response.status_code == 302
    assert "custom" in response.headers["Location"]


def test_set_country_empty_redirects_home(client):
    response = client.post("/set-country", data={"country_code": ""})
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_set_country_invalid_code_redirects_home(client):
    response = client.post("/set-country", data={"country_code": "INVALID_LONG_CODE"})
    assert response.status_code == 302


def test_set_country_custom_without_name_redirects_home(client):
    response = client.post("/set-country", data={"country_code": "ZZ", "custom_country": ""})
    assert response.status_code == 302


# ── Role setting ──────────────────────────────────────────────────────────────

def test_set_role_voter(client):
    response = client.post("/set-role", json={"role": "Voter"})
    assert response.status_code == 200
    assert b"success" in response.data


def test_set_role_candidate(client):
    response = client.post("/set-role", json={"role": "Candidate"})
    assert response.status_code == 200


def test_set_role_learner(client):
    response = client.post("/set-role", json={"role": "Learner"})
    assert response.status_code == 200


def test_set_role_invalid(client):
    response = client.post("/set-role", json={"role": "Admin"})
    assert response.status_code == 400


def test_set_role_empty(client):
    response = client.post("/set-role", json={"role": ""})
    assert response.status_code == 400


def test_set_role_missing_field(client):
    response = client.post("/set-role", json={})
    assert response.status_code == 400


def test_set_role_persists_in_session(client):
    client.post("/set-role", json={"role": "Candidate"})
    with client.session_transaction() as sess:
        assert sess.get("role") == "Candidate"


# ── Feature pages ─────────────────────────────────────────────────────────────

def test_timeline_loads(client):
    response = client.get("/dashboard/IN/timeline")
    assert response.status_code == 200


def test_glossary_loads(client):
    response = client.get("/dashboard/IN/glossary")
    assert response.status_code == 200


def test_myths_loads(client):
    response = client.get("/dashboard/IN/myths")
    assert response.status_code == 200


def test_quiz_page_loads(client):
    response = client.get("/dashboard/IN/quiz")
    assert response.status_code == 200


def test_chat_page_loads(client):
    response = client.get("/dashboard/IN/chat")
    assert response.status_code == 200


def test_checklist_page_loads(client):
    response = client.get("/dashboard/IN/checklist")
    assert response.status_code == 200


def test_resources_page_loads(client):
    response = client.get("/dashboard/IN/resources")
    assert response.status_code == 200


def test_polling_booth_page_loads(client):
    response = client.get("/dashboard/IN/polling-booth")
    assert response.status_code == 200


def test_guided_flow_loads(client):
    response = client.get("/dashboard/IN/guided-flow")
    assert response.status_code == 200


# ── Feature pages — invalid country ──────────────────────────────────────────

def test_timeline_invalid_country_404(client):
    response = client.get("/dashboard/ZZ/timeline")
    assert response.status_code == 404


def test_glossary_invalid_country_404(client):
    response = client.get("/dashboard/ZZ/glossary")
    assert response.status_code == 404


def test_quiz_invalid_country_404(client):
    response = client.get("/dashboard/ZZ/quiz")
    assert response.status_code == 404


# ── Security headers ──────────────────────────────────────────────────────────

def test_security_headers_present(client):
    response = client.get("/")
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_404_page(client):
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404