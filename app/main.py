from fastapi import FastAPI
from app.api.health import router as health_router

from app.models.user import User
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.files import router as files_router
from app.models import file, user

app = FastAPI()

app.include_router(health_router)
app.include_router(users_router)

app.include_router(auth_router)

app.include_router(files_router)