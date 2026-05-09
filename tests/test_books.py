import pytest

def test_add_book_success(auth_client, mock_db):
    mock_db["books"].find_one.return_value = None
    
    class MockInsertResult:
        inserted_id = "test_id_123"
        
    mock_db["books"].insert_one.return_value = MockInsertResult()
    
    response = auth_client.post("/books", json={
        "title": "New Book",
        "author": "Author",
        "isbn": "978-3-16-148410-0",
        "category": "Fiction",
        "total_copies": 10,
        "available_copies": 5
    })
    
    assert response.status_code == 200
    assert response.json() == {"message": "Book added", "id": "test_id_123"}
    mock_db["books"].insert_one.assert_called_once()
    mock_db["logs"].insert_one.assert_called_once()

def test_add_book_already_exists(auth_client, mock_db):
    mock_db["books"].find_one.return_value = {"isbn": "978-3-16-148410-0"}
    
    response = auth_client.post("/books", json={
        "title": "New Book",
        "author": "Author",
        "isbn": "978-3-16-148410-0",
        "category": "Fiction",
        "total_copies": 10,
        "available_copies": 5
    })
    
    assert response.status_code == 400
    assert response.json() == {"detail": "Book already exists"}
    mock_db["books"].insert_one.assert_not_called()
