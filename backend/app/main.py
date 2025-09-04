from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from .downloader import download_audio, get_output_file
from .tagger import tag_mp3
import os

app = FastAPI()

# 👇 CORS setup
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Which frontends can talk to backend
    allow_credentials=True,
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


@app.get("/download")
def download(youtube_url: str = Query(..., description="YouTube video link")):
    info = download_audio(youtube_url)
    mp3_file = get_output_file(info)
    tag_mp3(mp3_file, info)
    return FileResponse(mp3_file, filename=f"{info['title']}.mp3")
