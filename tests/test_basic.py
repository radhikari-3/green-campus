import pytest
from app import create_app

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login(client):
    response = client.get('/auth/login')
    assert response.status_code == 200