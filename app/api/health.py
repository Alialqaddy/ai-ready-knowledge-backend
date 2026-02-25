from fastapi import APIRouter, Depends
from sqlalchemy.orm import session, Session
from app.db.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def health(db: Session = Depends(get_db)):
    return {"status": "ok"}