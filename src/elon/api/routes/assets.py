"""Asset upload + public-ish serving for media URL handoff to platform APIs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from elon.api.deps import current_user, db_session
from elon.core.models import Asset, User
from elon.core.storage import ensure_bucket, get_object, put_object, sha256

router = APIRouter(prefix="/assets", tags=["assets"])


class UploadOut(BaseModel):
    asset_id: str
    s3_key: str


@router.post("/upload", response_model=UploadOut)
async def upload(
    file: UploadFile,
    user: User = Depends(current_user),
    db: Session = Depends(db_session),
) -> UploadOut:
    ensure_bucket()
    data = await file.read()
    digest = sha256(data)
    ext = (file.filename or "").rsplit(".", 1)[-1] or "bin"
    key = f"tenants/{user.tenant_id}/uploads/{digest}.{ext}"
    put_object(key, data, content_type=file.content_type)
    mime = file.content_type or "application/octet-stream"
    kind = "image" if mime.startswith("image/") else (
        "video" if mime.startswith("video/") else (
            "pdf" if mime == "application/pdf" else (
                "audio" if mime.startswith("audio/") else "doc"
            )
        )
    )
    asset = Asset(
        tenant_id=user.tenant_id, kind=kind, s3_key=key, mime=mime, hash=digest, source="uploaded",
    )
    db.add(asset)
    db.commit()
    return UploadOut(asset_id=str(asset.id), s3_key=key)


@router.get("/raw/{full_key:path}")
def raw(full_key: str) -> Response:
    """Public read for platform APIs that need a URL. The path is the S3 key.
    NOTE: in production, replace with a CDN-fronted bucket and signed URLs.
    """
    try:
        data = get_object(full_key)
    except Exception as e:
        raise HTTPException(404, f"not found: {e}") from e
    return Response(content=data, media_type="application/octet-stream")
