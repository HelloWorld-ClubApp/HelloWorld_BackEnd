from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import quote
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.config import settings


@dataclass(frozen=True)
class StoredObject:
    object_key: str
    file_url: str


def is_remote_file_url(file_url: str) -> bool:
    return file_url.startswith("http://") or file_url.startswith("https://")


def get_original_name(filename: Optional[str], fallback: str = "upload") -> str:
    original_name = Path(filename or fallback).name
    return original_name or fallback


def build_object_key(original_name: str, folder: str = "uploads") -> str:
    safe_folder = folder.strip("/")
    stored_name = f"{uuid4().hex}{Path(original_name).suffix.lower()}"
    return f"{safe_folder}/{stored_name}" if safe_folder else stored_name


def build_public_file_url(object_key: str) -> str:
    if settings.SUPABASE_STORAGE_PUBLIC_BASE_URL:
        base_url = settings.SUPABASE_STORAGE_PUBLIC_BASE_URL.rstrip("/")
    elif settings.SUPABASE_URL:
        bucket = settings.SUPABASE_STORAGE_BUCKET.strip("/")
        base_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{bucket}"
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL or SUPABASE_STORAGE_PUBLIC_BASE_URL is required.",
        )

    return f"{base_url}/{quote(object_key, safe='/')}"


def add_download_query(file_url: str, filename: str) -> str:
    separator = "&" if "?" in file_url else "?"
    return f"{file_url}{separator}download={quote(filename)}"


def get_s3_client():
    missing_settings = [
        name
        for name, value in {
            "SUPABASE_S3_ENDPOINT": settings.SUPABASE_S3_ENDPOINT,
            "SUPABASE_S3_ACCESS_KEY_ID": settings.SUPABASE_S3_ACCESS_KEY_ID,
            "SUPABASE_S3_SECRET_ACCESS_KEY": settings.SUPABASE_S3_SECRET_ACCESS_KEY,
        }.items()
        if not value
    ]
    if missing_settings:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Missing Supabase S3 settings: {', '.join(missing_settings)}",
        )

    try:
        import boto3  # type: ignore[import-not-found]
        from botocore.config import Config  # type: ignore[import-not-found]
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="boto3 is not installed. Install dependencies from requirements.txt.",
        ) from exc

    return boto3.client(
        "s3",
        endpoint_url=settings.SUPABASE_S3_ENDPOINT,
        region_name=settings.SUPABASE_S3_REGION,
        aws_access_key_id=settings.SUPABASE_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.SUPABASE_S3_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def upload_bytes_to_storage(
    *,
    content: bytes,
    original_name: str,
    content_type: str,
    folder: str = "uploads",
) -> StoredObject:
    object_key = build_object_key(original_name=original_name, folder=folder)

    try:
        get_s3_client().put_object(
            Bucket=settings.SUPABASE_STORAGE_BUCKET,
            Key=object_key,
            Body=content,
            ContentType=content_type,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Supabase Storage upload failed: {exc.__class__.__name__}",
        ) from exc

    return StoredObject(
        object_key=object_key,
        file_url=build_public_file_url(object_key),
    )
