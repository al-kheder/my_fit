from http.client import HTTPException

import pytest
from app.authentications import security
from jose import jwt


def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30

def test_create_access_token():
    token =security.create_access_token("ali@example.net")
    assert {"sub":"ali@example.net"}.items() <=jwt.decode(            # <= is a subset of...  e.g. dict1 <= dict2
        token,
        key=security.SECRET_KEY,
        algorithms=[security.ALGORITHM]
    ).items()


def test_hash_password():
    """Test the hash_password function."""
    password = "testpassword"
    hashed_password = security.hash_password(password)
    assert hashed_password != password
    assert security.verify_password(password, hashed_password)


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

#test for successful authentication
@pytest.mark.anyio
async def test_get_current_user(registered_user:dict):
    """Test the get_current_user function."""
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user is not None
    assert user["email"] == registered_user["email"]

#test for not valid
@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalid_token")