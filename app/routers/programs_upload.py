import gc
import uuid
from http import HTTPStatus
from random import randint
from typing import List

import httpx
from fastapi import APIRouter, HTTPException, UploadFile
from sqlalchemy import select, and_, func, update

from app.models import ProgramsUpload, Psychologist
from app.routers import Session
from app.schema.programs_upload import ProgramsUploadSchema, ProgramsUploadGenerateSchema
from app.service.minio import upload_file_to_minio, BUCKET_PROGRAMS_NAME, delete_file_from_minio, \
    get_file_url_from_minio, copy_file_from_minio, get_file_bytes_from_minio
from app.service.pdf import convert_doc_to_pdf, extract_cover_from_pdf, merge_pdfs, convert_image_to_pdf

router = APIRouter(prefix="/programs", tags=["programs"], redirect_slashes=True)


@router.get("/{id_psychologist}", response_model=List[ProgramsUploadSchema])
async def find_by_id_psychologist(id_psychologist: int, session: Session):
    db_programs = (await session.scalars(
        select(ProgramsUpload).where(
            ProgramsUpload.id_psychologist == id_psychologist).where(ProgramsUpload.generated == False)
        .order_by(ProgramsUpload.sequence)
    )).all()

    if not db_programs:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")

    results = []
    for program in db_programs:
        program_identifier = program.name.split('.')[0]
        program_schema = filter(lambda p: p.name.split('.')[0] == program_identifier, results)
        program_schema = next(program_schema, None)
        if not program_schema:
            program_schema = ProgramsUploadSchema.model_validate(program)
            results.append(program_schema)
        program_link = get_file_url_from_minio(program.name, program.path, BUCKET_PROGRAMS_NAME)
        if program.path.endswith('cover'):
            program_schema.cover = program_link
        else:
            program_schema.pdf = program_link

    return results


@router.post("/upload/image/{id_psychologist}", status_code=HTTPStatus.CREATED,
             response_model=List[ProgramsUploadSchema])
async def create_upload_file_image(id_psychologist: int, session: Session, files: List[UploadFile]):
    db_psychologist = await session.scalar(
        select(Psychologist).where(Psychologist.id == id_psychologist)
    )

    if not db_psychologist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Psychologist not exists.'
        )

    for file in files:
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension not in ['jpg', 'jpeg', 'png']:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Invalid file extension {extension}.')
    max_sequence = await session.scalar(
        select(func.max(ProgramsUpload.sequence)).where(ProgramsUpload.id_psychologist == id_psychologist)
    )
    if max_sequence is None:
        max_sequence = 0
    else:
        max_sequence += 1

    stored_files = []
    for file in files:
        filename = file.filename.rsplit('.', 1)[0].lower()
        pdf_bytes = None
        img_bytes = await file.read()
        try:
            pdf_bytes = convert_image_to_pdf(img_bytes)
        except HTTPException as e:
            for db_program in stored_files:
                delete_file_from_minio(db_program.name, db_program.path, BUCKET_PROGRAMS_NAME)
            raise e

        uuid_str = str(uuid.uuid4())
        db_program = ProgramsUpload(
            filename=filename,
            sequence=max_sequence,
            name=f'{uuid_str}.pdf',
            generated=False,
            id_psychologist=id_psychologist,
            path=f'{id_psychologist}/{uuid_str}/pdf',
        )
        session.add(db_program)
        stored_files.append(db_program)

        upload_file_to_minio(pdf_bytes, 'application/pdf', db_program.name, db_program.path,
                             BUCKET_PROGRAMS_NAME)

        db_program = ProgramsUpload(
            filename=filename,
            sequence=max_sequence,
            name=f'{uuid_str}.png',
            generated=False,
            id_psychologist=id_psychologist,
            path=f'{id_psychologist}/{uuid_str}/cover',
        )
        session.add(db_program)
        stored_files.append(db_program)
        max_sequence += 1
        upload_file_to_minio(img_bytes, 'image/png', db_program.name, db_program.path,
                             BUCKET_PROGRAMS_NAME)

    await session.commit()
    results = []
    for program in stored_files:
        program_identifier = program.name.split('.')[0]
        program_schema = filter(lambda p: p.name.split('.')[0] == program_identifier, results)
        program_schema = next(program_schema, None)
        if not program_schema:
            program_schema = ProgramsUploadSchema.model_validate(program)
            results.append(program_schema)
        program_link = get_file_url_from_minio(program.name, program.path, BUCKET_PROGRAMS_NAME)
        if program.path.endswith('cover'):
            program_schema.cover = program_link
        else:
            program_schema.pdf = program_link
    return results


@router.post("/upload/image-link/{id_psychologist}", status_code=HTTPStatus.CREATED,
             response_model=List[ProgramsUploadSchema])
async def create_upload_url_image(id_psychologist: int, urls: List[str], session: Session):
    db_psychologist = await session.scalar(
        select(Psychologist).where(Psychologist.id == id_psychologist)
    )

    if not db_psychologist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Psychologist not exists.'
        )

    images = []
    for url in urls:
        async with httpx.AsyncClient() as client:
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "cache-control": "max-age=0",
                "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
                "sec-fetch-site": "none",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
            }

            response = await client.get(url, headers=headers, follow_redirects=True, timeout=20)
            response.raise_for_status()
            if not response.headers.get('content-type').startswith('image'):
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail='Only image url are supported.'
                )
            images.append({
                'bytes': response.content,
                'content_type': response.headers.get('Content-Type'),
            })

    for image in images:
        is_image = 'image' in image['content_type']
        if not is_image:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Invalid file, just images are supported.')

    images = list(map(lambda image: image['bytes'], images))
    max_sequence = await session.scalar(
        select(func.max(ProgramsUpload.sequence)).where(ProgramsUpload.id_psychologist == id_psychologist)
    )
    if max_sequence is None:
        max_sequence = 0
    else:
        max_sequence += 1

    stored_files = []
    for image_bytes in images:
        pdf_bytes = None
        try:
            pdf_bytes = convert_image_to_pdf(image_bytes)
        except HTTPException as e:
            for db_program in stored_files:
                delete_file_from_minio(db_program.name, db_program.path, BUCKET_PROGRAMS_NAME)
            raise e

        uuid_str = str(uuid.uuid4())
        filename = f'documment_{randint(1000000000, 9999999999)}'
        db_program = ProgramsUpload(
            filename=filename,
            sequence=max_sequence,
            name=f'{uuid_str}.pdf',
            generated=False,
            id_psychologist=id_psychologist,
            path=f'{id_psychologist}/{uuid_str}/pdf',
        )
        session.add(db_program)
        stored_files.append(db_program)

        upload_file_to_minio(pdf_bytes, 'application/pdf', db_program.name, db_program.path,
                             BUCKET_PROGRAMS_NAME)

        db_program = ProgramsUpload(
            filename=filename,
            sequence=max_sequence,
            name=f'{uuid_str}.png',
            generated=False,
            id_psychologist=id_psychologist,
            path=f'{id_psychologist}/{uuid_str}/cover',
        )
        session.add(db_program)
        stored_files.append(db_program)
        max_sequence += 1
        upload_file_to_minio(image_bytes, 'image/png', db_program.name, db_program.path,
                             BUCKET_PROGRAMS_NAME)

    await session.commit()
    results = []
    for program in stored_files:
        program_identifier = program.name.split('.')[0]
        program_schema = filter(lambda p: p.name.split('.')[0] == program_identifier, results)
        program_schema = next(program_schema, None)
        if not program_schema:
            program_schema = ProgramsUploadSchema.model_validate(program)
            results.append(program_schema)
        program_link = get_file_url_from_minio(program.name, program.path, BUCKET_PROGRAMS_NAME)
        if program.path.endswith('cover'):
            program_schema.cover = program_link
        else:
            program_schema.pdf = program_link
    return results


@router.post("/upload/pdf/{id_psychologist}", status_code=HTTPStatus.CREATED, response_model=List[ProgramsUploadSchema])
async def create_upload_file_pdf(id_psychologist: int, session: Session, files: List[UploadFile]):
    db_psychologist = await session.scalar(
        select(Psychologist).where(Psychologist.id == id_psychologist)
    )

    if not db_psychologist:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Psychologist not exists.'
        )

    for file in files:
        extension = file.filename.rsplit('.', 1)[1].lower()
        if extension not in ['doc', 'docx', 'pdf']:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f'Invalid file extension {extension}.')
    max_sequence = await session.scalar(
        select(func.max(ProgramsUpload.sequence)).where(ProgramsUpload.id_psychologist == id_psychologist)
    )
    if max_sequence is None:
        max_sequence = 0
    else:
        max_sequence += 1
    stored_files = []
    for file in files:
        filename = file.filename.rsplit('.', 1)[0].lower()
        extension = file.filename.rsplit('.', 1)[1].lower()
        pdf_bytes = None
        if extension in ['doc', 'docx']:
            doc_bytes = await file.read()
            try:
                pdf_bytes = convert_doc_to_pdf(doc_bytes, extension)
            except HTTPException as e:
                for db_program in stored_files:
                    delete_file_from_minio(db_program.name, db_program.path, BUCKET_PROGRAMS_NAME)
                raise e

        uuid_str = str(uuid.uuid4())
        db_program = ProgramsUpload(
            filename=filename,
            sequence=max_sequence,
            name=f'{uuid_str}.pdf',
            generated=False,
            id_psychologist=id_psychologist,
            path=f'{id_psychologist}/{uuid_str}/pdf',
        )
        session.add(db_program)
        stored_files.append(db_program)

        if not pdf_bytes:
            pdf_bytes = await file.read()
        upload_file_to_minio(pdf_bytes, 'application/pdf', db_program.name, db_program.path,
                             BUCKET_PROGRAMS_NAME)

        if not pdf_bytes:
            await file.seek(0)
            pdf_bytes = await file.read()
        cover_bytes = extract_cover_from_pdf(pdf_bytes)
        db_program = ProgramsUpload(
            filename=filename,
            sequence=max_sequence,
            name=f'{uuid_str}.png',
            generated=False,
            id_psychologist=id_psychologist,
            path=f'{id_psychologist}/{uuid_str}/cover',
        )
        session.add(db_program)
        stored_files.append(db_program)
        max_sequence += 1
        upload_file_to_minio(cover_bytes, 'image/png', db_program.name, db_program.path,
                             BUCKET_PROGRAMS_NAME)

    await session.commit()
    results = []
    for program in stored_files:
        program_identifier = program.name.split('.')[0]
        program_schema = filter(lambda p: p.name.split('.')[0] == program_identifier, results)
        program_schema = next(program_schema, None)
        if not program_schema:
            program_schema = ProgramsUploadSchema.model_validate(program)
            results.append(program_schema)
        program_link = get_file_url_from_minio(program.name, program.path, BUCKET_PROGRAMS_NAME)
        if program.path.endswith('cover'):
            program_schema.cover = program_link
        else:
            program_schema.pdf = program_link
    return results


@router.post("/generate/{id_psychologist}", status_code=HTTPStatus.CREATED, response_model=ProgramsUploadSchema)
async def get_unified_pdf(id_psychologist: int, files: List[ProgramsUploadGenerateSchema], session: Session):
    if any(p.name is None for p in files) or any(p.sequence is None for p in files):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="sequence and name are required for all files.")
    ids = list(map(lambda p: p.id, files))

    db_programs = (await session.scalars(
        select(ProgramsUpload).where(ProgramsUpload.id.in_(ids))

    )).all()
    if not db_programs:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Empty report.")

    db_names = sorted(set(map(lambda p: (p.name, p.sequence), db_programs)), key=lambda x: x[1])
    uploaded_names = list(map(lambda p: (p.name, p.sequence), files))
    db_program_generated = await session.scalar(
        select(ProgramsUpload).where(
            and_(ProgramsUpload.id_psychologist == id_psychologist, ProgramsUpload.generated == True))
    )

    programs_changed = db_names != uploaded_names
    report_generated = db_program_generated is not None

    if programs_changed and report_generated:
        programs = (await session.scalars(
            select(ProgramsUpload).where(
                and_(ProgramsUpload.generated == True, ProgramsUpload.id_psychologist == id_psychologist))
        )).all()
        for program in programs:
            delete_file_from_minio(program.name, program.path, BUCKET_PROGRAMS_NAME)
            await session.delete(program)
    should_generate = programs_changed or not report_generated

    if not should_generate:
        db_program_generated = await session.scalar(
            select(ProgramsUpload).where(
                and_(ProgramsUpload.id_psychologist == id_psychologist, ProgramsUpload.generated == True))
        )
        program_schema = ProgramsUploadSchema.model_validate(db_program_generated)
        program_link = get_file_url_from_minio(db_program_generated.name, db_program_generated.path,
                                               BUCKET_PROGRAMS_NAME)
        program_schema.pdf = program_link
        return program_schema

    for file in files:
        name = file.name.split('.')[0]
        await session.execute(
            update(ProgramsUpload)
            .where(ProgramsUpload.name.startswith(name))
            .values(sequence=file.sequence)
        )

    db_programs = (await session.scalars(
        select(ProgramsUpload).where(
            and_(ProgramsUpload.id_psychologist == id_psychologist, ProgramsUpload.path.endswith('pdf')))
        .order_by(ProgramsUpload.sequence.asc())
    )).all()

    pdf_bytes_list = []
    for program in db_programs:
        pdf_bytes = get_file_bytes_from_minio(program.name, program.path, BUCKET_PROGRAMS_NAME)
        pdf_bytes_list.append(pdf_bytes)
    final_pdf = merge_pdfs(pdf_bytes_list)
    uuid_str = str(uuid.uuid4())
    filename = 'report'
    db_program_generated = ProgramsUpload(
        filename=filename,
        sequence=-1,
        name=f'{uuid_str}.pdf',
        generated=True,
        id_psychologist=id_psychologist,
        path=f'{id_psychologist}/{uuid_str}/pdf',
    )
    session.add(db_program_generated)
    upload_file_to_minio(final_pdf, 'application/pdf', db_program_generated.name, db_program_generated.path,
                         BUCKET_PROGRAMS_NAME)
    await session.commit()
    program_generated_schema = ProgramsUploadSchema.model_validate(db_program_generated)
    generated_link = get_file_url_from_minio(db_program_generated.name, db_program_generated.path, BUCKET_PROGRAMS_NAME)
    program_generated_schema.pdf = generated_link
    del pdf_bytes
    del pdf_bytes_list
    del final_pdf
    gc.collect()
    return program_generated_schema


@router.delete('/{id_program_upload}', status_code=HTTPStatus.NO_CONTENT)
async def delete_program_upload(
        id_program_upload: int,
        session: Session
):
    db_program_upload = await session.scalar(
        select(ProgramsUpload).where(ProgramsUpload.id == id_program_upload)
    )

    if not db_program_upload:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")
    name = db_program_upload.name.split('.')[0]

    db_programs = (await session.scalars(
        select(ProgramsUpload).where(ProgramsUpload.name.startswith(name))
    )).all()
    for program in db_programs:
        await session.delete(program)
        delete_file_from_minio(program.name, program.path, BUCKET_PROGRAMS_NAME)

    db_program_generated = await session.scalar(
        select(ProgramsUpload).where(
            and_(ProgramsUpload.id_psychologist == db_programs[0].id_psychologist, ProgramsUpload.generated == True))
    )
    if db_program_generated:
        await session.delete(db_program_generated)
        delete_file_from_minio(db_program_generated.name, db_program_generated.path, BUCKET_PROGRAMS_NAME)

    deleted_sequence = db_program_upload.sequence
    next_programs = (await session.scalars(
        select(ProgramsUpload).where(ProgramsUpload.sequence > deleted_sequence)
    )).all()
    for program in next_programs:
        program.sequence = program.sequence - 1
    await session.commit()


@router.post('/duplicate/{id_program_upload}', status_code=HTTPStatus.CREATED)
async def duplicate_program(id_program_upload: int, session: Session):
    sub_query = select(func.split_part(ProgramsUpload.name, '.', 1)).where(
        ProgramsUpload.id == id_program_upload)

    db_programs_upload = (await session.scalars(
        select(ProgramsUpload).where(
            func.split_part(ProgramsUpload.name, '.', 1).like(
                sub_query.scalar_subquery()
            )
        )
    )).all()

    if not db_programs_upload:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Resource not exists.")

    current_sequence = db_programs_upload[0].sequence

    db_next_programs = (await session.scalars(
        select(ProgramsUpload).where(ProgramsUpload.sequence > current_sequence)
    )).all()

    for program in db_next_programs:
        program.sequence = program.sequence + 1

    uuid_str = str(uuid.uuid4())
    db_programs_upload_pdf: ProgramsUpload = next(filter(lambda p: 'pdf' in p.path, db_programs_upload))
    db_programs_upload_cover: ProgramsUpload = next(filter(lambda p: 'cover' in p.path, db_programs_upload))
    db_program = ProgramsUpload(
        filename=db_programs_upload_pdf.filename,
        sequence=current_sequence + 1,
        name=f'{uuid_str}.pdf',
        generated=False,
        id_psychologist=db_programs_upload_pdf.id_psychologist,
        path=f'{db_programs_upload_pdf.id_psychologist}/{uuid_str}/pdf',
    )
    session.add(db_program)
    copy_file_from_minio(db_programs_upload_pdf.name, db_programs_upload_pdf.path, db_program.name, db_program.path,
                         BUCKET_PROGRAMS_NAME)

    db_program = ProgramsUpload(
        filename=db_programs_upload_cover.filename,
        sequence=current_sequence + 1,
        name=f'{uuid_str}.png',
        generated=False,
        id_psychologist=db_programs_upload_cover.id_psychologist,
        path=f'{db_programs_upload_cover.id_psychologist}/{uuid_str}/cover',
    )
    session.add(db_program)
    copy_file_from_minio(db_programs_upload_cover.name, db_programs_upload_cover.path, db_program.name, db_program.path,
                         BUCKET_PROGRAMS_NAME)

    await session.commit()
