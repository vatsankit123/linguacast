from app.chunker.chunker import split_audio_ffmpeg
from pydub import AudioSegment

input_file = "uploads/Power_English_Update.mp3"
chunk_paths = split_audio_ffmpeg(input_file, chunk_length_sec=30)

print("✅ Chunks created:\n")
for path in chunk_paths:
    audio = AudioSegment.from_file(path)
    duration_sec = round(len(audio) / 1000, 2)  # milliseconds to seconds
    print(f"{path} - {duration_sec} seconds")
