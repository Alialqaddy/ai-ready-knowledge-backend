from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter,HTTPException, status, Query
from app.db.database import get_db
from app.models.user import User
from pydantic import BaseModel, Field, EmailStr
from ..schemas.user import UserOut
from app.core.security import hash_password
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=6, max_length=72)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    is_active: Optional[bool] = None

@router.post("/", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):


    existing_email = db.query(User).filter(User.email == payload.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )


    existing_username = db.query(User).filter(User.username == payload.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )

    new_user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    email: str | None = Query(None),
    username: str | None = Query(None),
    password: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if (
        email is None
        and username is None
        and password is None
        and is_active is None
    ):
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided for update",
        )

    if email is not None:
        existing = db.query(User).filter(User.email == email).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=409, detail="Email already exists")
        user.email = email

    if username is not None:
        existing = db.query(User).filter(User.username == username).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=409, detail="Username already exists")
        user.username = username

    if password is not None:
        user.hashed_password = hash_password(password)

    if is_active is not None:
        user.is_active = is_active

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()
    return {"ok": True,"message": "User deleted successfully"}