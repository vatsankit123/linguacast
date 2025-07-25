from fastapi import UploadFile, HTTPException

ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav"]
ALLOWED_VIDEO_TYPES = ["video/mpeg", "video/mp4", "video/mov", "video/mkv"]


def validate_audio_file(file: UploadFile):
    if file.content_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    if file.content_type in ALLOWED_VIDEO_TYPES:
        return "video"
    return "invalid"