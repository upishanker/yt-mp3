import os
import yt_dlp

# Use absolute paths for deployed environments
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def download_audio(youtube_url: str) -> dict:
    """
    Downloads a single YouTube video as MP3 and returns metadata.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",
        "noplaylist": True,
        "playlist_items": "1",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
        ],
        # Add timeout and retry options
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,
        # Suppress some output
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            # If it's a playlist, yt-dlp may still return a dict with 'entries'
            if "entries" in info:
                info = info["entries"][0]  # pick first entry
            return info
    except Exception as e:
        print(f"Download failed: {e}")
        raise Exception(f"Failed to download audio: {str(e)}")

def get_output_file(info: dict) -> str:
    """
    Builds the path to the downloaded MP3 file.
    """
    title = info["title"]
    # Sanitize filename for cross-platform compatibility
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return os.path.join(DOWNLOADS_DIR, f"{safe_title}.mp3")