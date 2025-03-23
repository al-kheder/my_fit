from typing import List
from fastapi import FastAPI

from app.models.workout_schema import UserWorkoutIn, UserWorkoutOut
from datetime import date

app = FastAPI()


workout_table = {}


@app.post("/", response_model=UserWorkoutOut)
async def add_workout(workout: UserWorkoutIn):
    last_record_id = len(workout_table)
    new_workout = {**workout.dict(), "id": last_record_id}
    workout_table[last_record_id] = new_workout
    return new_workout

@app.get("/", response_model=List[UserWorkoutOut])
async def read_workouts():
    return list(workout_table.values())  # Convert dict values to list

@app.get("/{workout_id}", response_model=UserWorkoutOut)
async def read_workout(workout_id: int):
    return workout_table[workout_id]

@app.put("/{workout_id}", response_model=UserWorkoutOut)
async def update_workout(workout_id: int, workout: UserWorkoutIn):
    workout_table[workout_id].update(workout.dict())
    return workout_table[workout_id]

@app.delete("/{workout_id}", response_model=UserWorkoutOut)
async def delete_workout(workout_id: int):
    return workout_table.pop(workout_id)
