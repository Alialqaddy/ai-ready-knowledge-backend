from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    original_name = Column(String, nullable=False)
    stored_name = Column(String, unique=True, index=True, nullable=False)

    content_type = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=False)

    sha256 = Column(String, index=True, nullable=True)

    storage_path = Column(String, nullable=False)  # relative path on disk

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)