from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient


# Test data
TEST_WORKOUT = {
    "workout_name": "Morning Run",
    "workout_type": "Running",
    "workout_date": "2023-10-01",
    "workout_duration": 30,
    "calories_burned": 300,
    "notes": "Felt great during the run.",
    "created_at": datetime.now().isoformat()
}
#helpper function to create a workout
async def add_workout(test_workout, async_client: AsyncClient) -> dict:
    """Helper function to create a workout."""
    response = await async_client.post(
        "/workout",
        json=test_workout
    )
    #assert response.status_code == 200
    return response.json()

# A fixture that runs before tests to automatically add a workout to the database.
@pytest.fixture
async def added_workout(async_client: AsyncClient):
    """Fixture to create a test workout before running a test."""
    return await add_workout(TEST_WORKOUT, async_client)




#start of the test
@pytest.mark.anyio
async def test_add_workout(async_client: AsyncClient):
    response = await async_client.post(
        "/workout",
        json = TEST_WORKOUT
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_get_all_workouts(async_client: AsyncClient, added_workout):
    """Test retrieving all workouts"""
    response = await async_client.get("/workout")

    assert response.status_code == 200
    workouts = response.json()

    assert isinstance(workouts, list)
    assert len(workouts) >= 1  # Should contain at least our fixture workout
    assert added_workout["id"] in [w["id"] for w in workouts]



#TODO
#create test
# to get a single workout
# delete a workout
# update a workout

