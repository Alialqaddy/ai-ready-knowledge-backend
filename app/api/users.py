from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field, EmailStr

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.core.security import hash_password
from app.core.deps import get_current_active_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


# --------- Schemas (Keep local for now) ---------
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(..., min_length=6, max_length=72)


# --------- Helpers ---------
def _ensure_unique_email(db: Session, email: str, exclude_user_id: int | None = None):
    existing = db.query(User).filter(User.email == email).first()
    if existing and (exclude_user_id is None or existing.id != exclude_user_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")


def _ensure_unique_username(db: Session, username: str, exclude_user_id: int | None = None):
    existing = db.query(User).filter(User.username == username).first()
    if existing and (exclude_user_id is None or existing.id != exclude_user_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --------- Me endpoints (Any logged-in user) ---------
@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me", response_model=UserOut)
def update_me(
    email: EmailStr | None = Query(None),
    username: str | None = Query(None),
    password: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if email is None and username is None and password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update",
        )

    if email is not None:
        _ensure_unique_email(db, str(email), exclude_user_id=current_user.id)
        current_user.email = str(email)

    if username is not None:
        _ensure_unique_username(db, username, exclude_user_id=current_user.id)
        current_user.username = username

    if password is not None:
        # NOTE: password validation is best in schema, but since this is query-based:
        if len(password) < 6:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password too short")
        current_user.hashed_password = hash_password(password)

    db.commit()
    db.refresh(current_user)
    return current_user


# --------- Admin endpoints (Admin only) ---------
@router.post("/", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    _ensure_unique_email(db, str(payload.email))
    _ensure_unique_username(db, payload.username)

    new_user = User(
        email=str(payload.email),
        username=payload.username,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return _get_user_or_404(db, user_id)


@router.put("/{user_id}", response_model=UserOut)
def update_user_admin(
    user_id: int,
    email: EmailStr | None = Query(None),
    username: str | None = Query(None),
    password: str | None = Query(None),
    is_active: bool | None = Query(None),
    role: str | None = Query(None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = _get_user_or_404(db, user_id)

    if email is None and username is None and password is None and is_active is None and role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided for update",
        )

    if email is not None:
        _ensure_unique_email(db, str(email), exclude_user_id=user.id)
        user.email = str(email)

    if username is not None:
        _ensure_unique_username(db, username, exclude_user_id=user.id)
        user.username = username

    if password is not None:
        if len(password) < 6:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Password too short")
        user.hashed_password = hash_password(password)

    if is_active is not None:
        user.is_active = is_active

    if role is not None:
        # minimal validation
        if role not in ("user", "admin"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="role must be 'user' or 'admin'",
            )
        user.role = role

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    user = _get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
    return