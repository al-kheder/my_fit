import logging
from fastapi import APIRouter, Depends, HTTPException,status
from app.authentications.security import get_user_by_email, hash_password
from app.db.database import user_table, database
from app.models.users import UserIn


logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register",status_code=201,description="Register a new user with email and password")
async def register_user(user: UserIn):
    if await get_user_by_email(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = hash_password(user.password)
    query = user_table.insert().values(email=user.email,password=hashed_password)
    logger.debug("Inserting user into database: %s", user.email)

    await database.execute(query)
    return {"message": "User registered successfully", "email": user.email}

