from __future__ import annotations

import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.file import FileRecord
from app.schemas.file import FileOut
from app.services.storage import save_upload_file

router = APIRouter(prefix="/files", tags=["files"])


def _get_file_or_404(db: Session, file_id: int) -> FileRecord:
    rec = db.query(FileRecord).filter(FileRecord.id == file_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="File not found")
    return rec


def _assert_owner_or_admin(rec: FileRecord, current_user: User) -> None:
    if rec.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")


@router.post("/upload", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    uploaded: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):

    if not uploaded or not uploaded.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    stored_name, storage_path, size, sha = await save_upload_file(uploaded)

    rec = FileRecord(
        owner_id=current_user.id,
        original_name=uploaded.filename,
        stored_name=stored_name,
        content_type=uploaded.content_type,
        size_bytes=size,
        sha256=sha,
        storage_path=storage_path,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/", response_model=list[FileOut])
def list_my_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(FileRecord)
        .filter(FileRecord.owner_id == current_user.id)
        .order_by(FileRecord.id.desc())
        .all()
    )


@router.get("/{file_id}", response_model=FileOut)
def get_file_meta(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rec = _get_file_or_404(db, file_id)
    _assert_owner_or_admin(rec, current_user)
    return rec


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rec = _get_file_or_404(db, file_id)
    _assert_owner_or_admin(rec, current_user)

    path = rec.storage_path
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File missing on disk")

    return FileResponse(
        path=path,
        filename=rec.original_name,
        media_type=rec.content_type or "application/octet-stream",
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    rec = _get_file_or_404(db, file_id)
    _assert_owner_or_admin(rec, current_user)


    try:
        if rec.storage_path and os.path.exists(rec.storage_path):
            os.remove(rec.storage_path)
    except Exception:
        pass

    db.delete(rec)
    db.commit()
    return None