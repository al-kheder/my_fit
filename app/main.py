from fastapi import FastAPI
from app.routers.workouts import router as workout_router






app = FastAPI()

app.include_router(workout_router,tags=["workouts"])


