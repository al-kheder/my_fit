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
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)

goal_table = sqlalchemy.Table(
    "goals",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("goal_name", sqlalchemy.String),
    sqlalchemy.Column("workout_type", sqlalchemy.String),
    sqlalchemy.Column("calories_to_burn", sqlalchemy.Integer),
    sqlalchemy.Column("daily_target_calories", sqlalchemy.Integer),
    sqlalchemy.Column("daily_time_minutes", sqlalchemy.Integer),
    sqlalchemy.Column("duration_days", sqlalchemy.Integer),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False)
)




#TODO

weekly_plan_table = sqlalchemy.Table(
    "weekly_plans",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("week", sqlalchemy.Integer),
    sqlalchemy.Column("goal_focus", sqlalchemy.String),
    sqlalchemy.Column("nutrition_goal", sqlalchemy.String),
    sqlalchemy.Column("workout_goal", sqlalchemy.String),
    sqlalchemy.Column("habit_mindset_tip", sqlalchemy.String),
    sqlalchemy.Column("goal_id", sqlalchemy.ForeignKey("goals.id"), nullable=False)
)

goal_progress_table = sqlalchemy.Table(
    "goal_progress",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("goal_id", sqlalchemy.ForeignKey("goals.id"), nullable=False),
    sqlalchemy.Column("week", sqlalchemy.Integer),
    sqlalchemy.Column("nutrition_completed", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("workout_completed", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("habit_completed", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("notes", sqlalchemy.String),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now())
)



# Define progress table for storing AI analysis
progress_table = sqlalchemy.Table(
    "progress",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("goal_id", sqlalchemy.ForeignKey("goals.id"), nullable=False),
    sqlalchemy.Column("analysis_date", sqlalchemy.Date, default=sqlalchemy.func.now()),
    sqlalchemy.Column("analysis_result", sqlalchemy.Text),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=sqlalchemy.func.now())
)
# Create engine using the same URL as your database connection
# This is important for consistency
# Temporarily add this at the top of your database.py
logger.info("Current DATABASE_URL database.py: %s", config.DATABASE_URL)
engine = sqlalchemy.create_engine(config.DATABASE_URL)

# Create all tables
#TODO - delete drop_all when not needed
metadata.drop_all(engine)
#logger.info("Dropping all tables in the database")
metadata.create_all(engine)

# Database connection for async operations
database = databases.Database(
    config.DATABASE_URL,
    force_rollback=config.DB_FORCE_ROLLBACK
)