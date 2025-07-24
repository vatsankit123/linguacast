from fastapi import APIRouter, UploadFile, File
from uuid import uuid4
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from app.chunker.chunker import split_audio_ffmpeg
from app.transcriber.transcribe_chunks import transcribe_chunks
from app.worker.state import jobs

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)  # adjust workers as needed


def process_audio_task(file_path: str, job_id: str):
    try:
        jobs[job_id]["status"] = "processing"
        chunk_dir = split_audio_ffmpeg(file_path)
        result = transcribe_chunks(chunk_dir)

        # Cleanup
        shutil.rmtree(chunk_dir, ignore_errors=True)

        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = result

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Generate a new job_id
        job_id = str(uuid4())
        jobs[job_id] = {
            "status": "queued",
            "result": None,
            "error": None
        }

        # Submit the processing task
        executor.submit(process_audio_task, file_path, job_id)

        return {"job_id": job_id, "message": "Processing started"}

    except Exception as e:
        return {
            "error": str(e),
            "message": "An error occurred while starting processing."
        }


@router.get("/job-status/{job_id}")
async def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return {"error": "Invalid job_id"}
    return job

@router.get("/job_statuses/")
async def job_statuses():
    return jobs