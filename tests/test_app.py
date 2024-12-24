from app import app

def test_simplify_polynomial():
    client = app.test_client()
    response = client.post('/process_polynomial', json={
        "expression": "x^2 + 2x + 1",
        "userId": "123"
    })
    data = response.get_json()

    assert response.status_code == 200
    assert data['simplifiedExpression'] == 'x2 + 2x + 1'
    assert data['factoredExpression'] == '(x + 1)2'
    assert '-1.00000000000000' in data['roots']

def test_invalid_polynomial():
    client = app.test_client()
    response = client.post('/process_polynomial', json={
        "expression": "",
        "userId": "456"
    })
    data = response.get_json()

    assert response.status_code == 400
    assert 'Veuillez fournir une expression' in data['error']
