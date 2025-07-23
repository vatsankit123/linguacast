import os
import whisper
import re

# Load Whisper model once globally
model = whisper.load_model("base")

# Function to extract numbers from filenames for proper sorting
def extract_number(filename):
    match = re.search(r"_part(\d+)\.mp3", filename)
    return int(match.group(1)) if match else float('inf')

def transcribe_chunks(chunk_dir: str) -> dict:
    output = {}

    # Sort files by extracted numeric part
    files = sorted(
        [f for f in os.listdir(chunk_dir) if f.endswith(".mp3")],
        key=extract_number
    )

    for filename in files:
        path = os.path.join(chunk_dir, filename)
        print(f"\n🔊 Transcribing: {filename}")
        result = model.transcribe(path)
        output[filename] = result["text"]

    return output
