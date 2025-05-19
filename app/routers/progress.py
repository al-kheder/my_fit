import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from fastapi.encoders import jsonable_encoder

from app.models.progress import OverallSummary
from app.models.users import User
from app.authentications.security import get_current_user
from app.db.database import database, workout_table, goal_table, progress_summary_table

router = APIRouter()
logger = logging.getLogger(__name__)

def convert_datetime_fields(data: dict) -> dict:
    """Convert datetime objects to ISO format strings"""
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, list):
            data[key] = [convert_datetime_fields(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict):
            data[key] = convert_datetime_fields(value)
    return data

@router.get("/workout-summary",response_model=OverallSummary, description="Get combined workout and goal data for the current user")
async def get_workout_progress_summary(current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Generating workout and goal summary for user: {current_user.id}")

    try:
        # Fetch workouts for the user
        workout_query = workout_table.select().where(workout_table.c.user_id == current_user.id)
        workouts = await database.fetch_all(workout_query)

        # Fetch goals for the same user
        goal_query = goal_table.select().where(goal_table.c.user_id == current_user.id)
        goals = await database.fetch_all(goal_query)

        # Calculate summary statistics
        total_duration_user_workout = sum(w["workout_duration"] for w in workouts)
        total_calories_user_workout = sum(w["calories_burned"] for w in workouts)
        total_workouts = len(workouts)

        # Process goals data
        active_goals = [dict(goal) for goal in goals]
        total_calories_user_goal = sum(g["calories_to_burn"] for g in goals)
        total_duration_user_goal = sum(g["daily_time_minutes"] for g in goals)

        remaining_duration_to_goal = max(total_duration_user_goal - total_duration_user_workout, 0)
        remaining_calories_to_goal = max(total_calories_user_goal - total_calories_user_workout, 0)

        # Prepare workouts list with serialized datetime fields
        workouts_list = [convert_datetime_fields(dict(w)) for w in workouts]

        # Construct the summary object
        summary = {
            "user_id": current_user.id,
            "total_workouts": total_workouts,
            "total_duration": total_duration_user_workout,
            "total_calories_burned": total_calories_user_workout,
            "remaining_duration_to_goal": remaining_duration_to_goal,
            "remaining_calories_to_goal": remaining_calories_to_goal,
            "active_goals": active_goals,
            "workouts": workouts_list
        }

        # Save to the database
        query = progress_summary_table.insert().values(summary)
        logger.info(f"Saving workout summary to database for user: {current_user.id}")
        await database.execute(query)

        return jsonable_encoder(summary)

    except Exception as e:
        logger.error(f"Error in get_workout_progress_summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))