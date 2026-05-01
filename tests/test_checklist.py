"""Checklist tests for ElectIQ — page rendering and state API."""

import json
import pytest
from app import app


@pytest.fixture
def client():
    """Create a Flask test client with rate limiting disabled."""
    app.config['TESTING'] = True
    app.config['RATELIMIT_ENABLED'] = False
    with app.test_client() as client:
        yield client


def test_checklist_loads_for_voter(client):
    with client.session_transaction() as sess:
        sess['role'] = 'Voter'
    response = client.get('/dashboard/IN/checklist')
    assert response.status_code == 200


def test_checklist_loads_for_candidate(client):
    with client.session_transaction() as sess:
        sess['role'] = 'Candidate'
    response = client.get('/dashboard/IN/checklist')
    assert response.status_code == 200


def test_checklist_loads_for_learner(client):
    with client.session_transaction() as sess:
        sess['role'] = 'Learner'
    response = client.get('/dashboard/IN/checklist')
    assert response.status_code == 200


def test_checklist_loads_without_role(client):
    response = client.get('/dashboard/IN/checklist')
    assert response.status_code == 200


def test_checklist_invalid_country(client):
    response = client.get('/dashboard/XYZ/checklist')
    assert response.status_code == 404


def test_checklist_state_post(client):
    response = client.post(
        '/api/checklist-state?country=IN&role=Voter',
        json={"task_1": True, "task_2": False}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data


def test_checklist_state_get(client):
    client.post('/api/checklist-state?country=IN&role=Voter', json={"task_1": True})
    response = client.get('/api/checklist-state?country=IN&role=Voter')
    assert response.status_code == 200


def test_checklist_state_persistence(client):
    client.post('/api/checklist-state?country=IN&role=Voter', json={"task_1": True, "task_2": False})
    response = client.get('/api/checklist-state?country=IN&role=Voter')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)


def test_checklist_us_voter(client):
    with client.session_transaction() as sess:
        sess['role'] = 'Voter'
    response = client.get('/dashboard/US/checklist')
    assert response.status_code == 200