import datetime
import logging
from typing import Annotated
from fastapi import HTTPException,status, Depends
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, ExpiredSignatureError, JWTError

from app.db.database import database, user_table
from passlib.context import CryptContext
from app.app_configs.environment_config import config   # to get the secret key



logger = logging.getLogger(__name__)

SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES = config.SECRET_KEY, config.ALGORITHM, config.ACCESS_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
## This exception is raised when the credentials are not valid (avoid replication of code)
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# simplify the test for access_token_expire_minutes
def access_token_expire_minutes()-> int:
    return 30

pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(email: str) -> str:
    logger.debug("Creating access token for email: %s", email)
    expire  = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expire_minutes())
    jwt_payload = {"sub": email, "exp": expire}
    jwt_token = jwt.encode(jwt_payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_user_by_email(email: str):
    query = user_table.select().where(user_table.c.email == email)
    user = await database.fetch_one(query)
    if user:
        logger.debug("User found: %s", email)
    return user


## Authenticate user by checking if the email exists and if the password is correct
async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user:
       raise credentials_exception
    if not verify_password(password, user["password"]):
       raise credentials_exception
    return user

async def get_current_user(token:Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise credentials_exception
    user = await get_user_by_email(email=email)
    if user is None: # not found in the db
        raise credentials_exception
    return user