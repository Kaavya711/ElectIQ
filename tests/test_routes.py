"""Route smoke tests for ElectIQ — covers landing page, dashboard, country selection, and role setting."""

import pytest
from app import app


@pytest.fixture
def client():
    """Create a Flask test client with rate limiting disabled."""
    app.config['TESTING'] = True
    app.config['RATELIMIT_ENABLED'] = False
    with app.test_client() as client:
        yield client


def test_landing_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Understand Elections." in response.data
    assert b"Select your country" in response.data


def test_dashboard_india_loads(client):
    response = client.get('/dashboard/IN')
    assert response.status_code == 200
    assert b"India" in response.data


def test_dashboard_us_loads(client):
    response = client.get('/dashboard/US')
    assert response.status_code == 200
    assert b"United States" in response.data


def test_invalid_country_returns_404(client):
    response = client.get('/dashboard/XYZ')
    assert response.status_code == 404


def test_empty_country_returns_404(client):
    response = client.get('/dashboard/')
    assert response.status_code == 404


def test_set_country_redirects_known(client):
    response = client.post('/set-country', data={'country_code': 'US'})
    assert response.status_code == 302
    assert '/dashboard/US' in response.headers['Location']


def test_set_country_redirects_custom(client):
    response = client.post('/set-country', data={'country_code': 'custom', 'custom_country': 'Narnia'})
    assert response.status_code == 302
    assert 'custom' in response.headers['Location']


def test_set_country_empty_redirects_home(client):
    response = client.post('/set-country', data={'country_code': ''})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


def test_set_role_voter(client):
    response = client.post('/set-role', json={'role': 'Voter'})
    assert response.status_code == 200
    assert b'success' in response.data


def test_set_role_candidate(client):
    response = client.post('/set-role', json={'role': 'Candidate'})
    assert response.status_code == 200


def test_set_role_learner(client):
    response = client.post('/set-role', json={'role': 'Learner'})
    assert response.status_code == 200


def test_set_role_invalid(client):
    response = client.post('/set-role', json={'role': 'Admin'})
    assert response.status_code == 400


def test_timeline_loads(client):
    response = client.get('/dashboard/IN/timeline')
    assert response.status_code == 200


def test_glossary_loads(client):
    response = client.get('/dashboard/IN/glossary')
    assert response.status_code == 200


def test_myths_loads(client):
    response = client.get('/dashboard/IN/myths')
    assert response.status_code == 200


def test_quiz_page_loads(client):
    response = client.get('/dashboard/IN/quiz')
    assert response.status_code == 200


def test_chat_page_loads(client):
    response = client.get('/dashboard/IN/chat')
    assert response.status_code == 200


def test_checklist_page_loads(client):
    response = client.get('/dashboard/IN/checklist')
    assert response.status_code == 200


def test_resources_page_loads(client):
    response = client.get('/dashboard/IN/resources')
    assert response.status_code == 200


def test_polling_booth_page_loads(client):
    response = client.get('/dashboard/IN/polling-booth')
    assert response.status_code == 200
    