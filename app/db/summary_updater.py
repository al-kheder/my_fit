import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from fastapi.encoders import jsonable_encoder

from app.models.users import User
from app.authentications.security import get_current_user
from app.db.database import database, workout_table, goal_table, progress_summary_table,user_table
from app.routers.progress import convert_datetime_fields


logger = logging.getLogger(__name__)





async def find_workout_by_user_id(user_id):
    query = user_table.select().where(user_table.c.id == user_id)
    user = await database.fetch_one(query)
    return user


async def update_workout_summary(user_id: int):
    logger.info(f"Updating workout with ID: {user_id}")
    # Check if workout exists
    existing_user = await find_workout_by_user_id(user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")


    logger.info(f"Updating workout and goal summary for user: {user_id}")

    try:
        # Fetch workouts for the user
        workout_query = workout_table.select().where(workout_table.c.user_id == user_id)
        workouts = await database.fetch_all(workout_query)

        # Fetch goals for the same user
        goal_query = goal_table.select().where(goal_table.c.user_id == user_id)
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
            "user_id": user_id,
            "total_workouts": total_workouts,
            "total_duration": total_duration_user_workout,
            "total_calories_burned": total_calories_user_workout,
            "remaining_duration_to_goal": remaining_duration_to_goal,
            "remaining_calories_to_goal": remaining_calories_to_goal,
            "active_goals": active_goals,
            "workouts": workouts_list
        }

        # Save to the database
        query = progress_summary_table.update().where(
            progress_summary_table.c.user_id == user_id
        ).values(summary)
        logger.info(f"Saving workout summary to database for user: {user_id}")
        await database.execute(query)

        return jsonable_encoder(summary)

    except Exception as e:
        logger.error(f"Error in updating_workout_progress_summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

