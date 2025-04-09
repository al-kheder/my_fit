import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
os.environ["ENV_STATE"] = "dev"  # set the environment variable to test
from app.db.database import database
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





