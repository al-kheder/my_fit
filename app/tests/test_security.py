import pytest
from app.authentications import security



@pytest.mark.anyio
async def test_get_user(registered_user:dict):
    """Test the get_user_by_email function."""
    user = await security.get_user_by_email(registered_user["email"])
    assert user is not None
    assert user["email"] == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user_by_email("not_found@example.com")
    assert user is None