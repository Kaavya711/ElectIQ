import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Disable rate limiting for tests
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
    assert b"Dashboard" in response.data

def test_invalid_country_returns_404(client):
    response = client.get('/dashboard/XYZ')
    assert response.status_code == 404
    assert b"404 Page Not Found" in response.data

def test_change_country_redirects(client):
    response = client.post('/set-country', data={'country_code': 'US'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/dashboard/US'

def test_custom_country_redirects(client):
    response = client.post('/set-country', data={'country_code': 'custom', 'custom_country': 'Narnia'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/dashboard/custom?name=Narnia'
