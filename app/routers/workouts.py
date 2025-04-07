from fastapi import APIRouter, HTTPException
from app.models.workouts import UserWorkoutIn, UserWorkoutOut




router = APIRouter()

# Define a mock database for demonstration purposes
workout_table = {}

#create a workout
@router.post("/workout", response_model=UserWorkoutOut, status_code=201,description="add a new workout")
async def add_workout(workout: UserWorkoutIn):
    # Check if the workout already exists
    if workout.workout_name in workout_table:
        raise HTTPException(status_code=400, detail="Workout already exists")
    data = workout.dict()  # Convert the Pydantic model to a dictionary
    last_record_id = len(workout_table)
    # Insert the new workout into the mock database
    #workout_table[workout.id] = workout
    new_workout = {**data, "id": last_record_id}
    workout_table[last_record_id] = new_workout
    return new_workout


# Get all workouts
@router.get("/workout", response_model=list[UserWorkoutOut],description="get all workouts")
async def get_all_workouts():
    if not workout_table:
        raise HTTPException(status_code=404, detail="No workouts found")

    return list(workout_table.values())






