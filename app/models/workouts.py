from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel,Field,ConfigDict

# workout Create (POST request), it will be used to control the returned data
class UserWorkoutIn(BaseModel):
    model_config = ConfigDict(from_attributes=True) # make the pydantic to treat it as object as well as dict
    workout_name: str = Field(...,max_length=100,json_schema_extra={"example": "Morning Run"})
    workout_type: str = Field(...,json_schema_extra={"example": "Running"})
    workout_date: date = Field(...,json_schema_extra={"example": "2025-06-02"})  # Date in YYYY-MM-DD format
    workout_duration: int = Field(15,gt=0,json_schema_extra={"example": 30})  # Duration in minutes and must be positive gt : greater than
    calories_burned: int = Field(100,gt=0,json_schema_extra={"example": 350})  # Calories burned must be positive
    notes: Optional[str] = Field(None,max_length=500 ,json_schema_extra={"example": "Felt great during the run."})
    user_id: int
   # created_at: datetime

#Workout response (GET request)
class UserWorkoutOut(UserWorkoutIn):
    id: int
    #user_id: int  # Ensure workouts belong to a specific user


