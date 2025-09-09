# YouTube to Tagged MP3 Converter

A full-stack application that downloads YouTube videos as MP3 files with enhanced metadata tagging and custom album art support.

## Features

- 🎵 Download YouTube videos as high-quality MP3 files
- 🏷️ Automatic metadata extraction and tagging
- 🎨 Custom album art upload support
- 🔍 Enhanced artist detection using MusicBrainz API
- 🎯 Smart title parsing for better artist/song separation

## Tech Stack

**Backend:**
- FastAPI (Python)
- yt-dlp for YouTube downloading
- FFmpeg for audio conversion
- Mutagen for MP3 tagging
- MusicBrainz API for metadata enhancement

**Frontend:**
- Next.js
- React
- TypeScript

## Prerequisites

Before running this application, make sure you have:

- Python 3.8+ installed
- Node.js 16+ and npm installed
- FFmpeg installed on your system
  - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - **macOS:** `brew install ffmpeg`
  - **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/upishanker/yt-mp3.git
cd yt-mp3
```

### 2. Backend Setup

#### Navigate to backend directory and create a virtual environment:
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

#### Install Python dependencies:
```bash
pip install -r requirements.txt
```

#### Start the backend
```bash
uvicorn app.main:app --reload --port 8000
```
The backend API will be available at: `http://localhost:8000`


### 3. Frontend Setup

#### Navigate to your frontend directory:

```bash
cd ../frontend
```

#### Install dependencies
```bash
npm install
npm install next react react-dom
npm install -D typescript @types/react @types/node
```
#### Start the Frontend Server

```bash
npm run dev
```

Access the site from `http://localhost:3000`

