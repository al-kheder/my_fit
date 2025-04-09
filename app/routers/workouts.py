import logging

from fastapi import APIRouter, HTTPException
from app.models.workouts import UserWorkoutIn, UserWorkoutOut

from app.db.database import database, workout_table


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
async def add_workout(workout: UserWorkoutIn):
    # Check if the workout already exists
    existing_workout = await find_workout_by_name(workout.workout_name)
    if existing_workout:
        raise HTTPException(status_code=400, detail="Workout already exists")
    data = workout.model_dump()  # Convert the Pydantic model to a dictionary
    query = workout_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    generated_workout = {**data, "id": last_record_id}
    return generated_workout



# Get all workouts
@router.get("/workout", response_model=list[UserWorkoutOut],description="get all workouts")
async def get_all_workouts():
    query = workout_table.select()
    logger.debug(query)
    workouts = await database.fetch_all(query)
    return workouts


#TODO
#Add a workout (requires authentication)

#Get a workout (requires authentication)
# Get a workout by ID. (requires ownership)
#Update a workout.     (requires ownership)
#Delete a workout.     (requires ownership)
#




