from pydantic import BaseModel, Field,ConfigDict
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta



class OverallSummary(BaseModel):
    total_workouts: int
    total_calories_burned: float
    #total_minutes: float
    #active_days: int
    #active_goals: int
    #goals_on_track: int = 0
    #goals_completed: int = 0
    #workout_types: Dict[str, Dict[str, Union[int, float]]]
    #average_daily_calories: float
    #average_workout_duration: float
    #max_streak: int = 0
    #current_streak: int = 0