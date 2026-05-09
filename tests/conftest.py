import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

# Add app to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from main import app

@pytest.fixture
def mock_db():
    mock_books = AsyncMock()
    mock_members = AsyncMock()
    mock_borrow = AsyncMock()
    mock_users = AsyncMock()
    mock_logs = AsyncMock()

    # Patch modules where they are imported
    with patch('routers.books_collection', mock_books), \
         patch('routers.members_collection', mock_members), \
         patch('routers.borrow_collection', mock_borrow), \
         patch('routers.users_collection', mock_users), \
         patch('routers.logs_collection', mock_logs), \
         patch('logger.logs_collection', mock_logs):

        yield {
            "books": mock_books,
            "members": mock_members,
            "borrow": mock_borrow,
            "users": mock_users,
            "logs": mock_logs,
        }

@pytest.fixture
def client(mock_db):
    return TestClient(app)

@pytest.fixture
def auth_client(client):
    # Mock verify_token dependency or just patch the auth route behavior
    # For testing, we can override dependencies
    from auth import verify_token
    app.dependency_overrides[verify_token] = lambda: "testuser"
    yield client
    app.dependency_overrides.clear()
