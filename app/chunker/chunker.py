import os
import math
import subprocess
from pydub import AudioSegment

def split_audio_ffmpeg(input_path, chunk_length_sec=30):
    base_filename = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = os.path.join("chunks", base_filename)
    os.makedirs(output_dir, exist_ok=True)

    audio = AudioSegment.from_file(input_path)
    duration_sec = math.ceil(len(audio) / 1000)
    total_chunks = math.ceil(duration_sec / chunk_length_sec)

    chunk_paths = []

    for i in range(total_chunks):
        start = i * chunk_length_sec
        out_path = os.path.join(output_dir, f"{base_filename}_part{i+1}.mp3")

        command = [
            "ffmpeg", "-y", "-i", input_path,
            "-ss", str(start), "-t", str(chunk_length_sec),
            "-acodec", "copy", out_path
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        chunk_paths.append(out_path)

    return output_dir
