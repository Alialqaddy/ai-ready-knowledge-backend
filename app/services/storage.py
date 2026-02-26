from __future__ import annotations

import os
import re
import uuid
import hashlib
from pathlib import Path
from typing import Tuple, Optional

from fastapi import UploadFile, HTTPException


UPLOAD_DIR = os.getenv("UPLOAD_DIR", "storage/uploads")


MAX_UPLOAD_BYTES: Optional[int] = (
    int(os.getenv("MAX_UPLOAD_BYTES")) if os.getenv("MAX_UPLOAD_BYTES") else None
)


CHUNK_SIZE = 1024 * 1024  # 1MB


def _safe_filename(name: str) -> str:

    name = name.strip().replace("\\", "/")
    name = name.split("/")[-1]  # remove any path
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name or "file"


async def save_upload_file(uploaded: UploadFile) -> Tuple[str, str, int, Optional[str]]:

    if not uploaded or not uploaded.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    original = _safe_filename(uploaded.filename)


    suffix = Path(original).suffix.lower()


    stored_name = f"{uuid.uuid4().hex}{suffix}"

    base_dir = Path(UPLOAD_DIR)
    base_dir.mkdir(parents=True, exist_ok=True)

    dest_path = base_dir / stored_name

    hasher = hashlib.sha256()
    total = 0

    try:
        with dest_path.open("wb") as f:
            while True:
                chunk = await uploaded.read(CHUNK_SIZE)
                if not chunk:
                    break

                total += len(chunk)
                if MAX_UPLOAD_BYTES is not None and total > MAX_UPLOAD_BYTES:

                    try:
                        f.close()
                        if dest_path.exists():
                            dest_path.unlink()
                    except Exception:
                        pass
                    raise HTTPException(status_code=413, detail="File too large")

                hasher.update(chunk)
                f.write(chunk)

    finally:

        try:
            await uploaded.seek(0)
        except Exception:
            pass

    sha256_hex = hasher.hexdigest() if total > 0 else None

    # رجّع path كـ string طبيعي للـ OS (ويندوز \ ، لينكس /)
    return stored_name, str(dest_path), total, sha256_hex