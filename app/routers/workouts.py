import logging

from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated

from app.db.summary_updater import update_workout_summary
from app.models.workouts import UserWorkoutIn, UserWorkoutOut
from app.models.users import User
from app.authentications.security import get_current_user,oauth2_scheme

from app.db.database import database, workout_table
#from app.db.queries import update_progress_summary


router = APIRouter()

# Define a mock database for demonstration purposes
#workout_table = {}

logger = logging.getLogger(__name__)



async def find_workout_by_id(workout_id):
    query = workout_table.select().where(workout_table.c.id == workout_id)
    workout = await database.fetch_one(query)
    return workout
async def find_workout_by_name(workout_name):
    query = workout_table.select().where(workout_table.c.workout_name == workout_name)
    workout = await database.fetch_one(query)
    return workout

#create a workout
@router.post("/workout", response_model=UserWorkoutOut, status_code=201,description="add a new workout")
async def add_workout(workout: UserWorkoutIn,current_user:Annotated[User, Depends(get_current_user)]):
    logger.info("Adding a new workout: %s", workout.workout_name)
    # user need to be registered in order to add a workout
    # Check if the workout already exists
    existing_workout = await find_workout_by_name(workout.workout_name)
    if existing_workout:
        raise HTTPException(status_code=400, detail="Workout already exists")
    data = {**workout.model_dump(),"user_id":current_user.id}  # Convert the Pydantic model to a dictionary
    query = workout_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    generated_workout = {**data, "id": last_record_id}
    # update the workout summary
    await update_workout_summary(current_user.id)

    return generated_workout




# Get all workouts
@router.get("/workout", response_model=list[UserWorkoutOut], description="Get all workouts for current user")
async def get_all_workouts(current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Getting all workouts for user: {current_user.id}")
    query = workout_table.select().where(workout_table.c.user_id == current_user.id)
    logger.debug(query)
    workouts = await database.fetch_all(query)
    return workouts

# Get a specific workout by ID
@router.get("/workout/{workout_id}", response_model=UserWorkoutOut, description="Get a specific workout")
async def get_workout_by_id(workout_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Getting workout with ID: {workout_id}")

    # Check if workout exists
    existing_workout = await find_workout_by_id(workout_id)
    if not existing_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Check if user owns this workout
    if existing_workout["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this workout")

    return existing_workout

# Update a workout
@router.put("/workout/{workout_id}", response_model=UserWorkoutOut, description="Update a workout")
async def update_workout(workout_id: int, workout_update: UserWorkoutIn, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Updating workout with ID: {workout_id}")
    # Check if workout exists
    existing_workout = await find_workout_by_id(workout_id)
    if not existing_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Check if user owns this workout
    if existing_workout["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workout")

    # Update the workout
    data = {**workout_update.model_dump(), "user_id": current_user.id}
    query = workout_table.update().where(
        workout_table.c.id == workout_id
    ).values(**data)

    await database.execute(query)
    # update the workout summary
    await update_workout_summary(current_user.id)

    # Return the updated workout
    return {**data, "id": workout_id}


# Delete a workout
@router.delete("/workout/{workout_id}", status_code=204, description="Delete a workout")
async def delete_workout(workout_id: int, current_user: Annotated[User, Depends(get_current_user)]):
    logger.info(f"Deleting workout with ID: {workout_id}")

    # Check if workout exists
    existing_workout = await find_workout_by_id(workout_id)
    if not existing_workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    # Check if user owns this workout
    if existing_workout["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workout")

    # Delete the workout
    query = workout_table.delete().where(workout_table.c.id == workout_id)
    await database.execute(query)
    # update the workout summary
    await update_workout_summary(current_user.id)

    return None





