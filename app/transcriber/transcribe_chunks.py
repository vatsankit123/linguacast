import os
import whisper

def transcribe_chunks(chunk_dir: str) -> dict:
    output = ""

    model = whisper.load_model("base")  # safe: load inside thread

    for filename in sorted(os.listdir(chunk_dir), key=lambda x: int(''.join(filter(str.isdigit, x)))):
        if filename.endswith(".mp3"):
            path = os.path.join(chunk_dir, filename)
            print(f"\n🔊 Transcribing: {filename}")
            result = model.transcribe(path)
            output+= result["text"]

    return output
