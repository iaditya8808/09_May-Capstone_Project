import pytest

def test_register_success(client, mock_db):
    mock_db["users"].find_one.return_value = None
    
    response = client.post("/register", json={
        "username": "testuser",
        "password": "testpassword",
        "role": "MEMBER"
    })
    
    assert response.status_code == 200
    assert response.json() == {"message": "User registered"}
    mock_db["users"].insert_one.assert_called_once()
    mock_db["logs"].insert_one.assert_called_once()

def test_register_existing_user(client, mock_db):
    mock_db["users"].find_one.return_value = {"username": "testuser"}
    
    response = client.post("/register", json={
        "username": "testuser",
        "password": "testpassword",
        "role": "MEMBER"
    })
    
    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}
    mock_db["users"].insert_one.assert_not_called()

def test_login_success(client, mock_db):
    mock_db["users"].find_one.return_value = {"username": "testuser", "password": "testpassword"}
    
    response = client.post("/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password(client, mock_db):
    mock_db["users"].find_one.return_value = {"username": "testuser", "password": "correctpassword"}
    
    response = client.post("/login", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid password"}
