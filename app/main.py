from fastapi import FastAPI
from app.api.health import router as health_router
from app.db import database
app = FastAPI()
app.include_router(health_router)

