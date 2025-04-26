import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch, MagicMock

from app.main import app
from app.models.users import User
from app.AI.ai_agent import extract_fitness_goal

client = TestClient(app)

# Sample test data
mock_user = User(
    id=1,
    username="testuser",
    email="test@example.com",
    password="hashedpassword123"
)

mock_ai_response = """
{
    "goal_name": "Lose 2 kg in 5 months",
    "workout_type": "Mixed Cardio",
    "calories_to_burn": 15400,
    "duration_days": 150,
    "daily_target_calories": 102.67,
    "daily_time_minutes": 30
}
"""

@pytest.fixture
def mock_auth():
    with patch("app.authentications.security.get_current_user", return_value=mock_user):
        yield

@pytest.fixture
def mock_ai():
    with patch("app.routers.goals.create_custom_agent", return_value=mock_ai_response):
        yield

@pytest.fixture
def mock_database():
    with patch("app.routers.goals.database") as mock_db:
        # Mock fetch_one for find_goal_by_name to return None (no existing goal)
        mock_db.fetch_one.return_value = None
        # Mock execute for insert to return an ID
        mock_db.execute.return_value = 1
        yield mock_db

def test_add_goal_success(mock_auth, mock_ai, mock_database):
    """Test successful goal creation"""
    response = client.post("/goal?goal=lose%202%20kg%20in%205%20months")

    assert response.status_code == 201
    data = response.json()
    assert data["goal_name"] == "Lose 2 kg in 5 months"
    assert data["workout_type"] == "Mixed Cardio"
    assert data["calories_to_burn"] == 15400
    assert data["id"] == 1
    assert data["user_id"] == 1

def test_add_goal_duplicate(mock_auth, mock_ai, mock_database):
    """Test attempting to add a duplicate goal"""
    # Mock that the goal already exists
    mock_database.fetch_one.return_value = {"id": 2, "goal_name": "Lose 2 kg in 5 months"}

    response = client.post("/goal?goal=lose%202%20kg%20in%205%20months")

    assert response.status_code == 400
    assert response.json()["detail"] == "Your goal already exists"

def test_add_goal_invalid_ai_response(mock_auth, mock_database):
    """Test handling invalid AI response"""
    # Mock AI returning invalid JSON
    with patch("app.routers.goals.create_custom_agent", return_value="Not a valid JSON response"):
        response = client.post("/goal?goal=lose%202%20kg%20in%205%20months")

    assert response.status_code == 422
    assert "Invalid response from AI" in response.json()["detail"]

def test_add_goal_missing_authentication():
    """Test that authentication is required"""
    response = client.post("/goal?goal=lose%202%20kg%20in%205%20months")

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_extract_fitness_goal():
    """Test the extract_fitness_goal function directly"""
    # Valid JSON
    valid_json = '{"goal_name": "Test Goal", "workout_type": "Running", "calories_to_burn": 5000, "duration_days": 30, "daily_target_calories": 166.67, "daily_time_minutes": 20}'
    result = extract_fitness_goal(valid_json)
    assert result["goal_name"] == "Test Goal"
    assert result["workout_type"] == "Running"

    # Invalid JSON
    with pytest.raises(ValueError):
        extract_fitness_goal("Not a JSON string")

    # Missing required field
    with pytest.raises(KeyError):
        extract_fitness_goal('{"goal_name": "Test Goal"}')