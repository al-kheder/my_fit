import logging
from typing import Dict, Any
import json

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.AI.ai_agent import create_custom_agent, extract_fitness_goal
from app.models.goals import UserGoalIn,UserGoalOut
from app.models.users import User
from app.authentications.security import get_current_user,oauth2_scheme

from app.db.database import database, goal_table


router = APIRouter()
logger = logging.getLogger(__name__)

instruction_prompt="You are a fitness goal planner assistant. Based on the user's goal description below, return a JSON object with a detailed breakdown of their workout target. Use this format: goal_name: string, workout_type: string, calories_to_burn: integer, duration_days: integer, daily_target_calories: integer, daily_time_minutes: integer. Use these rules: 1 kg of fat = 7700 kcal. Estimate calorie burn rate based on the activity (e.g., Running ≈ 10 kcal/min, Walking ≈ 4 kcal/min, Cycling ≈ 8 kcal/min). Assume 5 workout days per week unless specified otherwise. Only return the JSON object, no explanation"



async def find_goal_by_id(goal_id):
    query = goal_table.select().where(goal_table.c.id == goal_id)
    goal = await database.fetch_one(query)
    return goal
async def find_goal_by_name(goal_name):
    query = goal_table.select().where(goal_table.c.goal_name == goal_name)
    goal = await database.fetch_one(query)
    return goal

#create a goal
@router.post("/goal", response_model=UserGoalOut, status_code=201, description="add a new goal")
async def add_goal(goal: str, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info("Adding a new goal: %s", goal)

    try:
        # Get raw response from AI agent (no await since it's not async)
        raw_response = create_custom_agent(instruction_prompt, goal_description=goal)

        # Log the raw response for debugging
        logger.info(f"Raw AI response: {raw_response}")

        # Extract structured data
        goal_data = extract_fitness_goal(raw_response)

        # Create a UserGoalIn instance with the extracted data
        goal_obj = UserGoalIn(
            goal_name=goal_data["goal_name"],
            workout_type=goal_data["workout_type"],
            calories_to_burn=goal_data["calories_to_burn"],
            daily_target_calories=goal_data["daily_target_calories"],
            daily_time_minutes=goal_data["daily_time_minutes"],
            duration_days=goal_data["duration_days"],
            user_id=current_user.id
        )

        # Check if the goal already exists
        existing_goal = await find_goal_by_name(goal_obj.goal_name)
        if existing_goal:
            raise HTTPException(status_code=400, detail="Your goal already exists")

        # Convert Pydantic model to dictionary before inserting
        goal_dict = goal_obj.model_dump()

        # Insert into database
        query = goal_table.insert().values(goal_dict)
        last_record_id = await database.execute(query)

        # Return the created goal with its ID
        return {**goal_dict, "id": last_record_id}

    except ValueError as e:
        logger.error(f"Error processing goal: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid response from AI: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")