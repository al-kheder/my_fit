from datetime import datetime
from typing import Optional

from pydantic import BaseModel,Field

# workout Create (POST request), it will be used to control the returned data
class UserWorkoutIn(BaseModel):
    workout_name: str = Field(...,max_length=100,example="Morning Run")
    workout_type: str = Field(...,example="Running")
    workout_date: str = Field(...,example="2023-10-01")
    workout_duration: int = Field(15,gt=0,example=30)  # Duration in minutes and must be positive gt : greater than
    calories_burned: int = Field(100,gt=0,example=300)  # Calories burned must be positive
    notes: Optional[str] = Field(None,max_length=500 ,example="Felt great during the run.")
    created_at: datetime

#Workout response (GET request)
class UserWorkoutOut(UserWorkoutIn):
    id: int
    #user_id: int  # Ensure workouts belong to a specific user
