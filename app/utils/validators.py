from fastapi import UploadFile, HTTPException

ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav"]

def validate_audio_file(file: UploadFile):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
