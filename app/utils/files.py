from http import HTTPStatus

from fastapi import HTTPException
from starlette.datastructures import UploadFile


async def read_upload_file(file: UploadFile, max_bytes: int) -> bytes:
    contents = bytearray()
    while chunk := await file.read(1024 * 1024):
        contents.extend(chunk)
        if len(contents) > max_bytes:
            raise HTTPException(
                status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                detail='File too large.',
            )
    return bytes(contents)