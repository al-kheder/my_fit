import uuid
from datetime import datetime, date
import pytest
from httpx import AsyncClient

from app.authentications import security

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
        "workout_name": f"Test-{uuid.uuid4().hex[:3]}",  # Removed extra space
        "workout_date": workout_data["workout_date"].isoformat(),  # Convert date to string

    }

async def add_workout(test_workout: dict, async_client: AsyncClient,logged_in_token:str) -> dict:
    """Helper to add a workout."""

    response = await async_client.post(
        "/workout",
        json=test_workout ,# Don't format again here
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    assert response.status_code == 201, f"Failed to add workout: {response.json()}"
    return response.json()

@pytest.fixture
async def added_workout(async_client: AsyncClient,registered_user:dict ,logged_in_token: str):
    """Fixture providing a pre-added workout."""
    workout_data = format_payload(TEST_WORKOUT)
    workout_data["user_id"] = registered_user["id"]
    return await add_workout(workout_data, async_client, logged_in_token)

@pytest.mark.anyio
async def test_add_workout(async_client: AsyncClient,registered_user:dict ,logged_in_token: str):
    workout_data = format_payload(TEST_WORKOUT)
    workout_data["user_id"] = registered_user["id"]
    response = await async_client.post(
        "/workout",
        json=workout_data,
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    assert response.status_code == 201
    # Complete assertion to verify response data,
    # This assertion checks that all the fields you sent in the request are correctly returned in the response,
    # and that an ID was generated for the workout.
    response_data = response.json()
    assert response_data["workout_name"] == workout_data["workout_name"]
    assert response_data["workout_type"] == workout_data["workout_type"]
    assert response_data["workout_date"] == workout_data["workout_date"]
    assert response_data["workout_duration"] == workout_data["workout_duration"]
    assert response_data["calories_burned"] == workout_data["calories_burned"]
    assert response_data["notes"] == workout_data["notes"]
    assert response_data["user_id"] == workout_data["user_id"]
    assert "id" in response_data

    #TODO: add assertions with full data , {"id": 1,...pass right data... ,"user_id": 1}.items() <= response.json().items()


# token is expired
@pytest.mark.anyio
async def test_add_workout_invalid_token(async_client: AsyncClient,registered_user:dict,mocker):
    # mocker allow us to modify the behavior of the function
    mocker.patch("app.authentications.security.access_token_expire_minutes",return_value = -1)
    token = security.create_access_token(registered_user["email"])
    response = await async_client.post(
        "/workout",
        json=format_payload(TEST_WORKOUT),
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]




@pytest.mark.anyio
async def test_get_all_workouts(async_client: AsyncClient, added_workout, logged_in_token: str):
    response = await async_client.get(
        "/workout",
    headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    assert response.status_code == 200

    workouts = response.json()
    assert isinstance(workouts, list)
    assert len(workouts) >= 1

@pytest.mark.anyio
async def test_update_workout(async_client: AsyncClient, added_workout, logged_in_token: str):
    """Test updating a workout."""
    workout_id = added_workout["id"]

    # Prepare updated data
    updated_data = {
        **added_workout,
        "workout_name": f"Updated-{uuid.uuid4().hex[:3]}",
        "workout_duration": 45,
        "notes": "Updated my workout notes"
    }

    # Update the workout
    response = await async_client.put(
        f"/workout/{workout_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    assert response.status_code == 200

    # Verify the update was applied
    updated_workout = response.json()
    assert updated_workout["workout_name"] == updated_data["workout_name"]
    assert updated_workout["workout_duration"] == 45
    assert updated_workout["notes"] == "Updated my workout notes"
    assert updated_workout["id"] == workout_id

@pytest.mark.anyio
async def test_update_workout_unauthorized(async_client: AsyncClient, added_workout):
    """Test that updating a workout fails without authentication."""
    workout_id = added_workout["id"]

    # Try to update without a token
    response = await async_client.put(
        f"/workout/{workout_id}",
        json=added_workout
    )

    assert response.status_code == 401

@pytest.mark.anyio
async def test_delete_workout(async_client: AsyncClient, added_workout, logged_in_token: str):
    """Test deleting a workout."""
    workout_id = added_workout["id"]

    # Delete the workout
    response = await async_client.delete(
        f"/workout/{workout_id}",
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    assert response.status_code == 204

    # Verify workout was deleted by trying to fetch it
    get_response = await async_client.get(
        f"/workout/{workout_id}",
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    assert get_response.status_code == 404

@pytest.mark.anyio
async def test_delete_workout_unauthorized(async_client: AsyncClient, added_workout):
    """Test that deleting a workout fails without authentication."""
    workout_id = added_workout["id"]

    # Try to delete without a token
    response = await async_client.delete(f"/workout/{workout_id}")

    assert response.status_code == 401

@pytest.mark.anyio
async def test_get_specific_workout(async_client: AsyncClient, added_workout, logged_in_token: str):
    """Test getting a specific workout by ID."""
    workout_id = added_workout["id"]

    # Get the workout
    response = await async_client.get(
        f"/workout/{workout_id}",
        headers={"Authorization": f"Bearer {logged_in_token}"}
    )

    assert response.status_code == 200
    workout = response.json()
    assert workout["id"] == workout_id
    assert workout["workout_name"] == added_workout["workout_name"]