import ffmpeg
import os

def extract_audio_from_video(file_path: str) -> str:
    """
    Extracts audio from a video file using ffmpeg and saves it as an MP3.
    Supports common formats like .mp4, .mpeg, .mov, .mkv, etc.

    :param file_path: Path to the input video file.
    :return: Path to the output audio file (.mp3). Returns empty string on failure.
    """
    if not os.path.isfile(file_path):
        print("Error: File does not exist.")
        return ""

    base, _ = os.path.splitext(file_path)
    audio_path = f"{base}.mp3"

    try:
        (
            ffmpeg
            .input(file_path)
            .output(audio_path, format='mp3', acodec='libmp3lame', vn=None)
            .overwrite_output()
            .run(quiet=True)
        )
        return audio_path
    except ffmpeg.Error as e:
        print("FFmpeg error:", e)
        return ""
