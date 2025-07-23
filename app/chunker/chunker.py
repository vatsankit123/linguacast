import os
import math
import subprocess
from pydub import AudioSegment

def split_audio_ffmpeg(input_path, chunk_length_sec=30):
    # Extract base filename without extension
    base_filename = os.path.splitext(os.path.basename(input_path))[0]

    # Create a dedicated chunk folder for this file
    output_dir = os.path.join("chunks", base_filename)
    os.makedirs(output_dir, exist_ok=True)

    # Load the audio file to get duration
    audio = AudioSegment.from_file(input_path)
    duration_sec = math.ceil(len(audio) / 1000)

    # Calculate number of chunks
    total_chunks = math.ceil(duration_sec / chunk_length_sec)

    for i in range(total_chunks):
        start = i * chunk_length_sec
        out_path = os.path.join(output_dir, f"{base_filename}_part{i+1}.mp3")

        # FFmpeg command to extract the chunk
        command = [
            "ffmpeg",
            "-y",                  # Overwrite output
            "-i", input_path,      # Input file
            "-ss", str(start),     # Start time
            "-t", str(chunk_length_sec),  # Duration
            "-acodec", "copy",     # Keep audio codec
            out_path               # Output chunk path
        ]

        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Return the chunk folder path
    return output_dir
