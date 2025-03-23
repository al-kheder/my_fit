from pydantic import BaseModel


class UserWorkoutIn(BaseModel):
    username: str
    workout_type: str
    workout_date: str
    workout_duration: int

class UserWorkoutOut(UserWorkoutIn):
    id: int

