from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel,Field,ConfigDict

# workout Create (POST request), it will be used to control the returned data
class UserGoalIn(BaseModel):
    model_config = ConfigDict(from_attributes=True) # make the pydantic to treat it as object as well as dict
    goal_name: str = Field(...,max_length=100,json_schema_extra={"example": "Lose 5 kg"})
    workout_type: str = Field(...,json_schema_extra={"example": "Running"})
    calories_to_burn: int = Field(100,gt=0,json_schema_extra={"example": 38350})  # Calories burned must be positive
    daily_target_calories: int = Field(100,gt=0,json_schema_extra={"example": 770})  # Calories burned must be positive
    daily_time_minutes: int = Field(15,gt=0,json_schema_extra={"example": 30})  # Duration in minutes and must be positive gt : greater than
    duration_days: int = Field(15,gt=0,json_schema_extra={"example": 90})  # Duration in days and must be positive gt : greater than
    user_id: int
   # created_at: datetime

#Workout response (GET request)
class UserGoalOut(UserGoalIn):
    id: int
    #user_id: int  # Ensure workouts belong to a specific user


