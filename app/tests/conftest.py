import os
from typing import AsyncGenerator, Generator

import uuid
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
os.environ["ENV_STATE"] = "dev"  # set the environment variable to test
from app.db.database import database, user_table
from app.main import app



@pytest.fixture(scope="session")  # make sure the test client is only created once and specify which async environment pytest uses
def anyio_backend():
    return "asyncio"


# to interact with the fastapi app without running the server
def client() -> Generator:
    yield TestClient(app)


# clear the database after each test
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect() # Rollback any changes made to the database during the test (undo any changes made to the database during the test)


@pytest.fixture()
async def async_client() -> AsyncGenerator:
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac



@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {
        "email": f"user_{uuid.uuid4().hex[:6]}@example.com",  # Added 'user_' prefix
        "password": "testpassword123!"  # Made more robust
    }

    # 1. Make registration request and verify success
    response = await async_client.post("/register", json=user_details)
    assert response.status_code == 201, f"Registration failed: {response.json()}"

    if response.status_code != 201:
        print(f"Response: {response.json()}")
        pytest.fail("Registration failed")

    # 2. Fetch user from database
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    assert user is not None, "User not found in database after registration"

    # 3. Add ID to user_details and return
    user_details["id"] = user.id  # Fixed dictionary access
    return user_details


