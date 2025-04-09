import uuid
from datetime import datetime, date
import pytest
from httpx import AsyncClient


# Test data
RAW_WORKOUT_DATE = date(2025, 10, 1)

TEST_WORKOUT = {
    "workout_name": "Morning Run",
    "workout_type": "Running",
    "workout_date": RAW_WORKOUT_DATE,
    "workout_duration": 30,
    "calories_burned": 300,
    "notes": "Felt great during the run.",
  #  "created_at": datetime.now().isoformat()
}

def format_payload(workout_data: dict) -> dict:
    """Format the workout data to be JSON serializable."""
    return {
        **workout_data,
        "workout_date": workout_data["workout_date"].isoformat()
    }

# Helper function to create a workout
async def add_workout(test_workout, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/workout",
        json=format_payload(test_workout)
    )
    return response.json()

# Fixture to add a workout before tests
@pytest.fixture
async def added_workout(async_client: AsyncClient):
    unique_workout = {
        **TEST_WORKOUT,
        "workout_name": f" Test-{uuid.uuid4().hex[:6]}"
    }
    return await add_workout(TEST_WORKOUT, async_client)


# Test creating a workout
@pytest.mark.anyio
async def test_add_workout(async_client: AsyncClient):
    response = await async_client.post(
        "/workout",
        json=format_payload(TEST_WORKOUT)
    )
    assert response.status_code == 201

#TODO  make sure the test is correct
# Test retrieving workouts
@pytest.mark.anyio
async def test_get_all_workouts(async_client: AsyncClient, added_workout):
    response = await async_client.get("/workout")
    assert response.status_code == 200

    workouts = response.json()
    assert isinstance(workouts, list)
    assert len(workouts) >= 1



#TODO
#make sure the test_get_workout is correct
#create test
# to get a single workout
# delete a workout
# update a workout

