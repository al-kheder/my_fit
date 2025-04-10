import uuid
from datetime import datetime, date
import pytest
from httpx import AsyncClient

# Test data
RAW_WORKOUT_DATE = date(2025, 10, 1)

TEST_WORKOUT = {
    "workout_name": "Morning Run",
    "workout_type": "Running",
    "workout_date": RAW_WORKOUT_DATE,  # date object
    "workout_duration": 30,
    "calories_burned": 300,
    "notes": "Felt great during the run.",
}

def format_payload(workout_data: dict) -> dict:
    """Format the workout data to be JSON serializable."""
    return {
        **workout_data,
        "workout_name": f"Test-{uuid.uuid4().hex[:6]}",  # Removed extra space
        "workout_date": workout_data["workout_date"].isoformat(),  # Convert date to string
    }

async def add_workout(test_workout: dict, async_client: AsyncClient) -> dict:
    """Helper to add a workout."""
    response = await async_client.post(
        "/workout",
        json=test_workout  # Don't format again here
    )
    assert response.status_code == 201, f"Failed to add workout: {response.json()}"
    return response.json()

@pytest.fixture
async def added_workout(async_client: AsyncClient):
    """Fixture providing a pre-added workout."""
    return await add_workout(format_payload(TEST_WORKOUT), async_client)

@pytest.mark.anyio
async def test_add_workout(async_client: AsyncClient):
    response = await async_client.post(
        "/workout",
        json=format_payload(TEST_WORKOUT)
    )
    assert response.status_code == 201

@pytest.mark.anyio
async def test_get_all_workouts(async_client: AsyncClient, added_workout):
    response = await async_client.get("/workout")
    assert response.status_code == 200

    workouts = response.json()
    assert isinstance(workouts, list)
    assert len(workouts) >= 1