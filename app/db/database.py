import logging
import databases
import sqlalchemy
from app.app_configs.environment_config import config


logger = logging.getLogger(__name__)

# Create SQLAlchemy metadata to store information about the database schema
metadata = sqlalchemy.MetaData()

# Define user table
user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(255), unique=True, index=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
)

# Define workout table
workout_table = sqlalchemy.Table(
    "workouts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("workout_name", sqlalchemy.String),
    sqlalchemy.Column("workout_type", sqlalchemy.String),
    sqlalchemy.Column("workout_duration", sqlalchemy.Integer),
    sqlalchemy.Column("calories_burned", sqlalchemy.Integer),
    sqlalchemy.Column("notes", sqlalchemy.String),
    sqlalchemy.Column("workout_date", sqlalchemy.DateTime),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
    #sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

# TODO - add user_id when create user table
goal_table = sqlalchemy.Table(
    "goals",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("description", sqlalchemy.String),
    sqlalchemy.Column("target_date", sqlalchemy.DateTime),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

# Create engine using the same URL as your database connection
# This is important for consistency
# Temporarily add this at the top of your database.py
logger.info("Current DATABASE_URL database.py: %s", config.DATABASE_URL)
engine = sqlalchemy.create_engine(config.DATABASE_URL)

# Create all tables
#TODO - delete drop_all when not needed
#metadata.drop_all(engine)
#logger.info("Dropping all tables in the database")
metadata.create_all(engine)

# Database connection for async operations
database = databases.Database(
    config.DATABASE_URL,
    force_rollback=config.DB_FORCE_ROLLBACK
)