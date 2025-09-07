from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .downloader import download_audio, get_output_file
from .tagger import tag_mp3, get_enhanced_metadata
import os
import uuid
import shutil

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://yt-mp3-iota.vercel.app",
    "https://yt-taggedmp3.fly.dev",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # Which frontends can talk to backend
    allow_credentials=True,
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)

# Use absolute paths for deployed environments
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Store session data temporarily
sessions = {}

class TagData(BaseModel):
    title: str
    artist: str
    album: str
    thumbnail: str = None


@app.get("/extract-info")
def extract_info(youtube_url: str = Query(..., description="YouTube video link")):
    """Extract metadata from YouTube video with enhanced artist detection"""
    try:
        info = download_audio(youtube_url)
        session_id = str(uuid.uuid4())

        # Get enhanced metadata
        enhanced_metadata = get_enhanced_metadata(info)

        # Store session data
        sessions[session_id] = {
            'info': info,
            'mp3_file': get_output_file(info)
        }

        return {
            'session_id': session_id,
            'tags': enhanced_metadata,
            'metadata_source': enhanced_metadata.get('source', 'basic'),
            'confidence': enhanced_metadata.get('confidence', 'unknown')
        }
    except Exception as e:
        print(f"Error in extract_info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract info: {str(e)}")
@app.post("/upload-image/{session_id}")
async def upload_image(session_id: str, file: UploadFile = File(...)):
    """Upload custom image for album art"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save uploaded file
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"{session_id}.{file_extension}"
    file_path = os.path.join(UPLOADS_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store file path in session
    sessions[session_id]['uploaded_image'] = file_path

    return {"message": "Image uploaded successfully", "filename": filename}

@app.post("/download/{session_id}")
def download_with_tags(session_id: str, tags: TagData):
    """Download MP3 with custom tags"""
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session_data = sessions[session_id]
        mp3_file = session_data['mp3_file']

        # Use uploaded image if available, otherwise use thumbnail URL
        thumbnail_source = session_data.get('uploaded_image') or tags.thumbnail

        # Create custom info dict with user-provided tags
        custom_info = {
            'title': tags.title,
            'uploader': tags.artist,
            'album': tags.album,
            'thumbnail': thumbnail_source
        }

        tag_mp3(mp3_file, custom_info)

        # Clean up session and uploaded file
        if 'uploaded_image' in session_data and os.path.exists(session_data['uploaded_image']):
            os.remove(session_data['uploaded_image'])
        del sessions[session_id]

        return FileResponse(mp3_file, filename=f"{tags.title}.mp3")
    except Exception as e:
        print(f"Error in download_with_tags: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download: {str(e)}")