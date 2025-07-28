# app/jobs.py
from enum import Enum
from typing import Dict, Any
from threading import Lock

class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"

_jobs: Dict[str, Dict[str, Any]] = {}
_lock = Lock()

def create_job(job_id: str):
    with _lock:
        _jobs[job_id] = {"status": JobStatus.pending, "result": None, "error": None}

def update_status(job_id: str, status: JobStatus, result: Any = None, error: str = None):
    with _lock:
        job = _jobs.get(job_id)
        if job:
            job["status"] = status
            job["result"] = result
            job["error"] = error

def get_job(job_id: str) -> Dict[str, Any]:
    with _lock:
        return _jobs.get(job_id, {"status": None, "result": {}, "error": None})
