import pytest
import sys
import os

# Add the parent directory to the Python path so app can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    # Set Flask config to testing mode
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'static/uploads_test'
    
    # Return a test client
    with app.test_client() as client:
        yield client

def test_login_page_loads(client):
    """
    Test that the login page loads successfully (HTTP status code 200)
    and contains the text 'Secure File System'
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Secure File System" in response.data

def test_dashboard_redirects_unauthenticated(client):
    """
    Test that access to the home/dashboard page without being logged in
    properly redirects (HTTP status code 302) to the login page
    """
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_logout_redirects(client):
    """
    Test that accessing /logout redirects the user to the login page
    """
    response = client.get('/logout')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
