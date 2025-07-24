from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from app.chunker.chunker import split_audio_ffmpeg
from app.transcriber.transcribe_chunks import transcribe_chunks
from app.worker.state import jobs
from app.utils.validators import validate_audio_file  # ✅ Custom validator

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)  # Adjust as needed

# 🔧 Background task: process audio
def process_audio_task(file_path: str, job_id: str):
    try:
        jobs[job_id]["status"] = "processing"
        
        # 1. Split audio into chunks
        chunk_dir = split_audio_ffmpeg(file_path)
        
        # 2. Transcribe chunks
        result = transcribe_chunks(chunk_dir)
        
        # 3. Clean up chunks
        shutil.rmtree(chunk_dir, ignore_errors=True)

        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = result

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

# 📥 Upload & process audio file
@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # 1. Validate audio file
        validate_audio_file(file)

        # 2. Save file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 3. Generate job ID and add to job registry
        job_id = str(uuid4())
        jobs[job_id] = {
            "status": "queued",
            "result": None,
            "error": None
        }

        # 4. Run background processing
        executor.submit(process_audio_task, file_path, job_id)

        return {
            "job_id": job_id,
            "message": "Processing started"
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📊 Get status of a specific job
@router.get("/job-status/{job_id}")
async def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Invalid job_id")
    return job

# 📊 Get all jobs and their statuses
@router.get("/job-statuses/")
async def job_statuses():
    return jobs
