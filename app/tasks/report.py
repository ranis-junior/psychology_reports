import os
from asyncio import create_subprocess_exec, subprocess, wait_for, Semaphore
from pathlib import Path
from uuid import uuid4

from taskiq import TaskiqDepends, Context
from taskiq.depends.progress_tracker import TaskProgress, TaskState

from app.service.minio import BUCKET_IDADI_NAME, upload_file_to_minio, get_file_url_from_minio
from app.settings import get_settings, Settings
from app.worker import broker

JAR_SEMAPHORE = Semaphore(1)


@broker.task
async def generate_jasper_report(jasper_file_name: str, parameters: dict, mode: str = 'PDF',
                                 settings: Settings = TaskiqDepends(get_settings), ctx: Context = TaskiqDepends()):
    await broker.result_backend.set_progress(
        ctx.message.task_id,
        TaskProgress(state=TaskState.STARTED, meta=None)
    )
    jar_name = os.path.join(settings.REPORT_JAR_PATH, settings.REPORT_JAR_NAME)
    report_base_dir = settings.REPORT_BASE_PATH
    db_username = settings.DB_USER
    db_password = settings.DB_PASSWORD
    db_host = settings.DATABASE_HOST
    db_name = settings.DATABASE_NAME
    uuid_out_name = str(uuid4())
    parameters_str = ':'.join(f'{k}={v}' for k, v in parameters.items()) if parameters else ''

    args = ['java', '-jar', jar_name, '--base-dir', report_base_dir, '--parameters', parameters_str, '--mode', mode,
            '--generate-from-file', jasper_file_name, '--db-username', db_username, '--db-password', db_password,
            '--db-host', db_host, '--db-database', db_name, '--pdf-output-name', uuid_out_name]
    try:
        async with JAR_SEMAPHORE:
            proc = await create_subprocess_exec(*args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = await wait_for(proc.communicate(), timeout=60)
            print(stdout)
            print(stderr)
        if mode.lower() == 'compile':
            return
        pdf_path = os.path.join(f'{report_base_dir}/pdf/', f'{uuid_out_name}.pdf')
        pdf_path = Path(pdf_path)
        pdf_bytes = pdf_path.read_bytes()
        pdf_path.unlink()
        upload_file_to_minio(pdf_bytes, 'application/pdf', uuid_out_name, 'pdf', BUCKET_IDADI_NAME)
        pdf_minio_url = get_file_url_from_minio(uuid_out_name, 'pdf', BUCKET_IDADI_NAME)
        await broker.result_backend.set_progress(
            ctx.message.task_id,
            TaskProgress(state=TaskState.SUCCESS, meta=None)
        )
        return pdf_minio_url
    except Exception as e:
        print(f"Generating report for {jasper_file_name}")
        print(f"Parameters: {parameters}")
        print(f"Settings: {settings}")
        print(f"mode: {mode}")
        print(f"Parameters STR: {parameters_str}")
        raise e
