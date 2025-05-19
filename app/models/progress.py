from pydantic import BaseModel, Field,ConfigDict
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta



class OverallSummary(BaseModel):
    id: int
    user_id: int
    total_workouts: int
    total_duration: int
    total_calories_burned: int
    remaining_duration_to_goal: int
    remaining_calories_to_goal: int
    active_goals: Optional[Dict] = None
    workouts: Optional[List[Dict]] = None