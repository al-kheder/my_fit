from pydantic import BaseModel, Field



class ProgressSummery(BaseModel):
    total_workouts: int = Field(..., example=50)
    total_calories_burned: int = Field(..., example=5000)
    average_duration: float = Field(..., example=45.5)  # Average duration in minutes
    average_calories_burned: float = Field(..., example=400.0)  # Average calories burned per workout
    active_goals: int = Field(..., example=3)  # Number of active goals
    completed_goals: int = Field(..., example=2)  # Number of completed goals
