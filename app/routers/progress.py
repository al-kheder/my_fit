import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.models.users import User
from app.models.goals import UserGoalOut
from app.models.workouts import WorkoutOut
from app.authentications.security import get_current_user
from app.db.database import database, goal_table, workout_table
from sqlalchemy import select, func, and_

router = APIRouter()
logger = logging.getLogger(__name__)

class ProgressSummary(dict):
    """Dictionary-like class to store progress summary data."""
    pass

async def get_user_goals(user_id: int) -> List[Dict]:
    """Retrieve all goals for a specific user."""
    query = goal_table.select().where(goal_table.c.user_id == user_id)
    return await database.fetch_all(query)

async def get_user_workouts(user_id: int, goal_id: Optional[int] = None,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> List[Dict]:
    """
    Retrieve workouts for a user, optionally filtered by goal and date range.
    """
    query = workout_table.select().where(workout_table.c.user_id == user_id)

    if goal_id:
        query = query.where(workout_table.c.goal_id == goal_id)

    if start_date:
        query = query.where(workout_table.c.date >= start_date)

    if end_date:
        query = query.where(workout_table.c.date <= end_date)

    return await database.fetch_all(query)

@router.get("/progress", response_model=List[ProgressSummary],
            description="Get a summary of user progress across all goals")
async def get_user_progress(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Returns a summary of the user's progress across all goals,
    including total calories burned and remaining calories to reach goals.
    """
    try:
        # Get all user goals
        goals = await get_user_goals(current_user.id)

        if not goals:
            return []

        progress_summaries = []

        for goal in goals:
            # Get workouts related to this goal
            workouts = await get_user_workouts(current_user.id, goal_id=goal["id"])

            # Calculate total calories burned for this goal
            total_calories_burned = sum(workout["calories_burned"] for workout in workouts)

            # Calculate remaining calories to reach the goal
            remaining_calories = max(0, goal["calories_to_burn"] - total_calories_burned)

            # Calculate progress percentage
            if goal["calories_to_burn"] > 0:
                progress_percentage = min(100, round((total_calories_burned / goal["calories_to_burn"]) * 100, 1))
            else:
                progress_percentage = 0

            # Calculate days elapsed and days remaining
            days_elapsed = len(set(workout["date"].date() for workout in workouts))
            days_remaining = max(0, goal["duration_days"] - days_elapsed)

            # Create summary
            summary = ProgressSummary({
                "goal_id": goal["id"],
                "goal_name": goal["goal_name"],
                "workout_type": goal["workout_type"],
                "target_calories": goal["calories_to_burn"],
                "total_calories_burned": total_calories_burned,
                "remaining_calories": remaining_calories,
                "progress_percentage": progress_percentage,
                "days_elapsed": days_elapsed,
                "days_remaining": days_remaining,
                "daily_target_calories": goal["daily_target_calories"],
                "daily_average_burned": round(total_calories_burned / max(1, days_elapsed), 1) if days_elapsed > 0 else 0,
                "workout_count": len(workouts),
                "is_on_track": (total_calories_burned / max(1, days_elapsed)) >= goal["daily_target_calories"] if days_elapsed > 0 else True
            })

            progress_summaries.append(summary)

        return progress_summaries

    except Exception as e:
        logger.error(f"Error retrieving progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve progress: {str(e)}")

@router.get("/progress/{goal_id}", response_model=ProgressSummary,
            description="Get detailed progress for a specific goal")
async def get_goal_progress(goal_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Returns detailed progress information for a specific goal,
    including time series data for trend analysis.
    """
    try:
        # Get the specific goal
        query = goal_table.select().where(
            and_(goal_table.c.id == goal_id, goal_table.c.user_id == current_user.id)
        )
        goal = await database.fetch_one(query)

        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        # Get all workouts for this goal
        workouts = await get_user_workouts(current_user.id, goal_id=goal_id)

        # Calculate basic stats
        total_calories_burned = sum(workout["calories_burned"] for workout in workouts)
        remaining_calories = max(0, goal["calories_to_burn"] - total_calories_burned)

        if goal["calories_to_burn"] > 0:
            progress_percentage = min(100, round((total_calories_burned / goal["calories_to_burn"]) * 100, 1))
        else:
            progress_percentage = 0

        # Calculate time-based metrics
        days_elapsed = len(set(workout["date"].date() for workout in workouts))
        days_remaining = max(0, goal["duration_days"] - days_elapsed)

        # Group workouts by day for daily trend
        workout_by_date = {}
        for workout in workouts:
            date_str = workout["date"].strftime("%Y-%m-%d")
            if date_str not in workout_by_date:
                workout_by_date[date_str] = 0
            workout_by_date[date_str] += workout["calories_burned"]

        # Create detailed summary
        summary = ProgressSummary({
            "goal_id": goal["id"],
            "goal_name": goal["goal_name"],
            "workout_type": goal["workout_type"],
            "target_calories": goal["calories_to_burn"],
            "total_calories_burned": total_calories_burned,
            "remaining_calories": remaining_calories,
            "progress_percentage": progress_percentage,
            "days_elapsed": days_elapsed,
            "days_remaining": days_remaining,
            "daily_target_calories": goal["daily_target_calories"],
            "daily_average_burned": round(total_calories_burned / max(1, days_elapsed), 1) if days_elapsed > 0 else 0,
            "workout_count": len(workouts),
            "is_on_track": (total_calories_burned / max(1, days_elapsed)) >= goal["daily_target_calories"] if days_elapsed > 0 else True,
            "daily_trend": workout_by_date,
            "recent_workouts": [
                {
                    "id": w["id"],
                    "name": w["name"],
                    "date": w["date"].strftime("%Y-%m-%d"),
                    "duration_minutes": w["duration_minutes"],
                    "calories_burned": w["calories_burned"]
                }
                for w in sorted(workouts, key=lambda x: x["date"], reverse=True)[:5]
            ]
        })

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving goal progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve goal progress: {str(e)}")

@router.get("/progress/summary", response_model=Dict[str, Any],
            description="Get overall fitness summary")
async def get_overall_summary(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Returns an overall summary of all user fitness activities across all goals.
    """
    try:
        # Get all user workouts without filtering by goal
        workouts = await get_user_workouts(current_user.id)

        if not workouts:
            return {
                "total_workouts": 0,
                "total_calories_burned": 0,
                "total_minutes": 0,
                "active_goals": 0
            }

        # Get all user goals
        goals = await get_user_goals(current_user.id)

        # Calculate aggregates
        total_calories = sum(workout["calories_burned"] for workout in workouts)
        total_minutes = sum(workout["duration_minutes"] for workout in workouts)

        # Get unique workout dates
        workout_dates = set(workout["date"].date() for workout in workouts)

        # Group workouts by type
        workout_types = {}
        for workout in workouts:
            workout_type = workout["type"]
            if workout_type not in workout_types:
                workout_types[workout_type] = {
                    "count": 0,
                    "total_calories": 0,
                    "total_minutes": 0
                }
            workout_types[workout_type]["count"] += 1
            workout_types[workout_type]["total_calories"] += workout["calories_burned"]
            workout_types[workout_type]["total_minutes"] += workout["duration_minutes"]

        # Calculate goal completion status
        completed_goals = sum(1 for goal in goals if
                              sum(w["calories_burned"] for w in workouts if w["goal_id"] == goal["id"])
                              >= goal["calories_to_burn"])

        return {
            "total_workouts": len(workouts),
            "total_calories_burned": total_calories,
            "total_minutes": total_minutes,
            "active_days": len(workout_dates),
            "active_goals": len(goals),
            "completed_goals": completed_goals,
            "workout_types": workout_types,
            "average_daily_calories": round(total_calories / max(1, len(workout_dates)), 1) if workout_dates else 0,
            "average_workout_duration": round(total_minutes / max(1, len(workouts)), 1) if workouts else 0
        }

    except Exception as e:
        logger.error(f"Error retrieving overall summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve overall summary: {str(e)}")