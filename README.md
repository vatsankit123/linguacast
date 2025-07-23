
# 🎙️ Linguacast

Linguacast is a fast and scalable audio transcription service built using **FastAPI**, **FFmpeg**, and **OpenAI Whisper**. It accepts audio files (MP3), splits them into chunks, transcribes each chunk, and returns the full transcription in JSON format.

---

## 🚀 Features

- Upload `.mp3` files via FastAPI endpoint
- Automatic chunking using `FFmpeg` (default: 30s per chunk)
- Transcription using Whisper (base model)
- Organized output with structured JSON
- Handles large audio files with ease

---

## 🛠️ Tech Stack

- Python 3.10+
- FastAPI
- Whisper (OpenAI)
- FFmpeg
- Pydub

---

## 📂 Folder Structure

linguacast/
├── app/
│ ├── api/
│ │ └── routes.py
│ ├── chunker/
│ │ └── chunker.py
│ ├── transcriber/
│ │ └── transcribe_chunks.py
├── uploads/
├── chunks/
├── main.py
└── README.md

