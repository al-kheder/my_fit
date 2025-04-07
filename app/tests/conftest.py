from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.routers.workouts import workout_table


@pytest.fixture(scope="session")  # make sure the test client is only created once and specify which async environment pytest uses
def anyio_backend():
    return "asyncio"


# to interact with the fastapi app without running the server
def client() -> Generator:
    yield TestClient(app)


# clear the database after each test
@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    workout_table.clear()
    yield



@pytest.fixture()
async def async_client() -> AsyncGenerator:
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        yield ac





