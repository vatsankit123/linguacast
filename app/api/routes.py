from fastapi import APIRouter, UploadFile, File
import os
from app.chunker.chunker import split_audio_ffmpeg
from app.transcriber.transcribe_chunks import transcribe_chunks

router = APIRouter()

@router.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # 1. Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)

        with open(file_path, "wb") as f:
            f.write(await file.read())

        print("✅ File saved:", file_path)

        # 2. Chunk the audio
        chunk_folder_path = split_audio_ffmpeg(file_path)
        print("✅ Chunks created in:", chunk_folder_path)

        # 3. Transcribe only this file’s chunks
        results = transcribe_chunks(chunk_folder_path)
        print("✅ Transcription done")

        # 4. Return the transcription
        return {
            "message": "File processed successfully",
            "filename": file.filename,
            "transcription": results
        }

    except Exception as e:
        print("❌ Error occurred during processing:", str(e))
        return {
            "error": str(e),
            "message": "An error occurred while processing the file."
        }
