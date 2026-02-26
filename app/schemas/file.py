from pydantic import BaseModel
from datetime import datetime


class FileOut(BaseModel):
    id: int
    owner_id: int
    original_name: str
    stored_name: str
    content_type: str | None
    size_bytes: int
    sha256: str | None
    storage_path: str
    created_at: datetime

    class Config:
        from_attributes = True