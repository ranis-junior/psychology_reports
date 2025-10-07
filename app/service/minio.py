import io
from datetime import timedelta, datetime, timezone
from http import HTTPStatus
from io import BytesIO
from typing import Any

from fastapi import HTTPException
from minio import Minio, S3Error
from minio.commonconfig import CopySource, Filter
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration

from app.settings import settings

MINIO_CLIENT = Minio(
    settings.MINIO_HOST,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)
BUCKET_PHOTO_NAME = "photos"
BUCKET_PROGRAMS_NAME = "programs"
BUCKET_IDADI_NAME = "idadi"

if not MINIO_CLIENT.bucket_exists(BUCKET_PHOTO_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_PHOTO_NAME)

if not MINIO_CLIENT.bucket_exists(BUCKET_PROGRAMS_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_PROGRAMS_NAME)

if not MINIO_CLIENT.bucket_exists(BUCKET_IDADI_NAME):
    MINIO_CLIENT.make_bucket(BUCKET_IDADI_NAME)
    MINIO_CLIENT.set_bucket_lifecycle(BUCKET_IDADI_NAME, LifecycleConfig([
        Rule(
            rule_id='expire-pdfs',
            status='Enabled',
            rule_filter=Filter(prefix="pdf/"),
            expiration=Expiration(days=1)
        )
    ]))


def upload_image_to_minio(file: bytes, content_type: str, image_name: str, image_path: str,
                          bucket_name: str = BUCKET_PHOTO_NAME):
    if not content_type.startswith("image/"):
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="Apenas imagens são permitidas!")

    upload_file_to_minio(file, content_type, image_name, image_path, bucket_name)


def upload_file_to_minio(file_bytes: bytes, content_type: str, file_name: str, file_path: str, bucket_name: str):
    file_bytes: BytesIO = io.BytesIO(file_bytes)
    filename = f"{file_path}/{file_name}"
    try:
        MINIO_CLIENT.put_object(
            bucket_name,
            filename,
            file_bytes,
            length=-1,
            part_size=10 * 1024 * 1024,
            content_type=content_type
        )
    except S3Error as e:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Erro no MinIO: {e}")


def get_file_url_from_minio(file_name: str, file_path: Any, bukect_name: str = BUCKET_PHOTO_NAME):
    url = MINIO_CLIENT.presigned_get_object(
        bukect_name,
        f"{file_path}/{file_name}",
        expires=timedelta(hours=1)
    )
    return url


def get_file_bytes_from_minio(file_name: str, file_path: Any, bukect_name: str = BUCKET_PHOTO_NAME):
    return MINIO_CLIENT.get_object(
        bukect_name,
        f"{file_path}/{file_name}",
    ).read()


def copy_file_from_minio(file_name_from: str, file_path_from: str, file_name_to: str, file_path_to: str,
                         bucket_name: str = BUCKET_PHOTO_NAME):
    obj = MINIO_CLIENT.copy_object(
        bucket_name,
        f"{file_path_to}/{file_name_to}",
        CopySource(bucket_name, f"{file_path_from}/{file_name_from}")
    )
    return obj


def delete_file_from_minio(file_name: str, file_path: str, bucket_name: str):
    filename = f"{file_path}/{file_name}"
    MINIO_CLIENT.remove_object(bucket_name, filename)
