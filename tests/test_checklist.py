import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['RATELIMIT_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_checklist_loads_for_voter(client):
    with client.session_transaction() as sess:
        sess['role'] = 'Voter'
    response = client.get('/dashboard/IN/checklist')
    assert response.status_code == 200
    assert b"Verify name at electoralsearch.eci.gov.in" in response.data

def test_checklist_loads_for_candidate(client):
    with client.session_transaction() as sess:
        sess['role'] = 'Candidate'
    response = client.get('/dashboard/IN/checklist')
    assert response.status_code == 200
    assert b"File Nomination (Form 2B)" in response.data

def test_checklist_state_api(client):
    # Test POST
    response = client.post('/api/checklist-state?country=IN&role=Voter', json={"v_r_1": True})
    assert response.status_code == 200
    
    # Test GET
    response = client.get('/api/checklist-state?country=IN&role=Voter')
    assert response.status_code == 200
