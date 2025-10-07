from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .worker import broker
import taskiq_fastapi

from app.routers import psychologists, patients, pti, pti_stimulus_area, pti_specific_objectives_topics, \
    pti_specific_objectives_subtopics, patient_record, idadi, idadi_domains, programs_upload

app = FastAPI()
taskiq_fastapi.init(broker, 'app.main:app')

origins = [
    'http://localhost:5173',
    'https://localhost:5173',
    'http://127.0.0.1:5173',
    'https://127.0.0.1:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
