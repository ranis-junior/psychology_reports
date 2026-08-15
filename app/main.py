import taskiq_fastapi
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers import psychologists, patients, pti, pti_stimulus_area, pti_specific_objectives_topics, \
    pti_specific_objectives_subtopics, patient_record, idadi, idadi_domains, programs_upload, idadi_form_question, \
    idadi_form_question_patient, users, auth
from app.service.minio import ensure_buckets
from app.settings import settings
from .worker import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_buckets()
    yield


app = FastAPI(lifespan=lifespan)
taskiq_fastapi.init(broker, 'app.main:app')

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(psychologists.router, prefix='/api')
app.include_router(patients.router, prefix='/api')
app.include_router(patient_record.router, prefix='/api')
pti.router.include_router(pti_stimulus_area.router, prefix='/api')
pti.router.include_router(pti_specific_objectives_topics.router, prefix='/api')
pti.router.include_router(pti_specific_objectives_subtopics.router, prefix='/api')
app.include_router(pti.router, prefix='/api')
app.include_router(idadi.router, prefix='/api')
app.include_router(idadi_domains.router, prefix='/api')
app.include_router(programs_upload.router, prefix='/api')
app.include_router(idadi_form_question.router, prefix='/api')
app.include_router(idadi_form_question_patient.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
