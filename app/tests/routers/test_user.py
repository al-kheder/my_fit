import pytest
from httpx import AsyncClient
import uuid

from sqlalchemy.orm import defer


async def register_user(async_client: AsyncClient, user_details: dict) -> dict:
    """Helper to register a user."""
    response = await async_client.post("/register", json=user_details)
    assert response.status_code == 201, f"Registration failed: {response.json()}"
    return response.json()


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    """Test user registration."""
    user_details = {
        "email": f"user_{uuid.uuid4().hex[:3]}@example.com /from register_user",
        "password": "automated_test123!"
    }

    response = await register_user(async_client, user_details)
    assert response["message"] == "User registered successfully"
    assert response["email"] == user_details["email"]


@pytest.mark.anyio
async def test_register_user_already_exists(async_client: AsyncClient, registered_user: dict):
    """Test user registration with an already registered email."""
    user_details = {
        "email": registered_user["email"],
        "password": "automated_test123!"
    }

    response = await async_client.post("/register", json=user_details)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"




@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    user_details = {
        "email": f"user_{uuid.uuid4().hex[:3]}@example.com /login user not exists",
        "password": "automated_test123!"
    }
    response = await async_client.post("/token", json=user_details)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient, registered_user: dict):
    """Test user registration with an already registered email."""
    user_details = {
        "email": registered_user["email"],
        "password":registered_user["password"]
    }
    response = await async_client.post("/token", json=user_details)
    assert response.status_code == 200
    assert response.json()["access_token"] is not None

