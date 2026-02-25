from fastapi import FastAPI
from app.api.health import router as health_router
from app.db.database import engine, Base
from app.models.user import User
from app.api.users import router as users_router
from app.api.auth import router as auth_router

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(health_router)
app.include_router(users_router)

app.include_router(auth_router)