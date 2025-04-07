from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional
#goal model
class GoalBase(BaseModel):
    description: str = Field(..., example="Lose 5 kg in 3 months")
    target_datetime: datetime

    @validator("target_datetime")
    def validate_future_date(cls, value: datetime) -> datetime:
        if value <= datetime.now():
            raise ValueError("Target datetime must be in the future")
        return value

#create goal (POST request)
class GoalCreate(GoalBase):
    pass

#Goeal responce (GET request)
class GoalResponse(GoalBase):
    id: int
    user_id: int
    is_completed: bool = Field(False, example=False)

