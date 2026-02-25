from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy.orm import Session
from app.core.config import SECRET_KEY, ALGORITHMS, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import verify_password
from app.models.user import User


def create_access_token(user_id: int, role: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "role": role, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHMS)

def authenticate_user(username: str, password: str, db: Session) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHMS])