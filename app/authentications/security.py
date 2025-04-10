import logging
from app.db.database import database, user_table


logger = logging.getLogger(__name__)

async def get_user_by_email(email: str):
    """
    Fetch a user by their email address.
    """
    query = user_table.select().where(user_table.c.email == email)
    user = await database.fetch_one(query)
    if user:
        logger.debug("User found: %s", email)
    return user