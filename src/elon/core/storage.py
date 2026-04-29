"""Object storage (MinIO/S3) helpers."""

from __future__ import annotations

import hashlib
from io import BytesIO

import boto3
from botocore.client import Config

from elon.core.settings import get_settings

_settings = get_settings()


def _client():
    return boto3.client(
        "s3",
        endpoint_url=_settings.s3_endpoint_url,
        aws_access_key_id=_settings.s3_access_key,
        aws_secret_access_key=_settings.s3_secret_key,
        region_name=_settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def ensure_bucket() -> None:
    c = _client()
    existing = {b["Name"] for b in c.list_buckets().get("Buckets", [])}
    if _settings.s3_bucket not in existing:
        c.create_bucket(Bucket=_settings.s3_bucket)


def put_object(key: str, data: bytes, content_type: str | None = None) -> str:
    extra = {"ContentType": content_type} if content_type else {}
    _client().put_object(Bucket=_settings.s3_bucket, Key=key, Body=data, **extra)
    return key


def get_object(key: str) -> bytes:
    obj = _client().get_object(Bucket=_settings.s3_bucket, Key=key)
    return obj["Body"].read()


def stream_to_bytes(stream) -> bytes:
    if isinstance(stream, (bytes, bytearray)):
        return bytes(stream)
    if isinstance(stream, BytesIO):
        return stream.getvalue()
    return stream.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
