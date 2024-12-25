import pytest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    """Fixture to set up the test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_complex_polynomial(client):
    """Test with a polynomial with complex roots."""
    response = client.post('/process_polynomial', json={
        "expression": "x2 + 1",
        "userId": "1"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data['roots'] == ['-i', 'i']
    assert data['simplifiedExpression'] == 'x2 + 1'
    assert data['factoredExpression'] == 'x2 + 1'


def test_missing_expression(client):
    """Test when no polynomial is provided."""
    response = client.post('/process_polynomial', json={
        "userId": "1"
    })
    data = response.get_json()
    assert response.status_code == 400
    assert data['error'] == "No polynomial provided"


def test_missing_user_id(client):
    """Test when no user ID is provided."""
    response = client.post('/process_polynomial', json={
        "expression": "x2 - 4"
    })
    data = response.get_json()
    assert response.status_code == 400
    assert data['error'] == "User ID is required"


def test_invalid_polynomial(client):
    """Test with an invalid polynomial expression."""
    response = client.post('/process_polynomial', json={
        "expression": "x2 + -",
        "userId": "1"
    })
    data = response.get_json()
    assert response.status_code == 500
    assert "error" in data


def test_constant_polynomial(client):
    """Test with a constant polynomial."""
    response = client.post('/process_polynomial', json={
        "expression": "4",
        "userId": "1"
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data['roots'] == []
    assert data['simplifiedExpression'] == '4'
    assert data['factoredExpression'] == '4'
