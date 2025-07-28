from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from uuid import uuid4
import os
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from app.chunker.chunker import split_audio_ffmpeg
from app.transcriber.transcribe_chunks import transcribe_chunks
from app.worker.state import jobs
from app.utils.validators import validate_audio_file
from app.utils.media_utils import extract_audio_from_video
from app.utils.llm_utils import generate_answer_and_update_result
from app.models import PromptObject

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=4)  # Adjust as needed

# 🔧 Background task: process audio
def process_audio_task(file_path: str, job_id: str, prompts: PromptObject):
    try:
        jobs[job_id]["status"] = "processing"
        
        # 1. Split audio into chunks
        chunk_dir = split_audio_ffmpeg(file_path)
        
        # 2. Transcribe chunks
        transcription = transcribe_chunks(chunk_dir)
        
        # 3. Clean up chunks
        shutil.rmtree(chunk_dir, ignore_errors=True)

        jobs[job_id]["result"]["transcription"] = transcription

        for key,value in prompts.prompts.items():
            jobs[job_id]["result"][key] = value
        print(jobs[job_id])

        generate_answer_and_update_result(jobs, job_id)


    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

def process_video_task(file_path: str, job_id: str, prompts: PromptObject):
    try:
        audio_file_path = extract_audio_from_video(file_path)
        executor.submit(process_audio_task, audio_file_path, job_id, prompts)
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

# 📥 Upload & process audio file
@router.post("/upload/")
async def upload(file: UploadFile = File(...), prompt: str = Form(...)):
    try:
        # 1. Validate file
        validated_file = validate_audio_file(file)

        # If invalid
        if validated_file=="invalid":
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
        
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
            "result": {},
            "error": None
        }
        try:
            prompt_dict = json.loads(prompt)
            prompt_obj = PromptObject(**{"prompts": prompt_dict["prompts"]})
            print(prompt_obj)
        except Exception as e:
            return {"error": str(e)}

        # 4. Run background processing
        if validated_file=="audio":
            executor.submit(process_audio_task, file_path, job_id, prompt_obj)

            return {
                "job_id": job_id,
                "message": "Processing started"
            }
        if validated_file=="video":
            executor.submit(process_video_task, file_path, job_id, prompt_obj)
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
