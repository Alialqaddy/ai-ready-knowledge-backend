from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str = Field(..., min_length=6, max_length=72)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"