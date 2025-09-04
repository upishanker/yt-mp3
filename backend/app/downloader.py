import os
import yt_dlp

DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)


def download_audio(youtube_url: str) -> dict:
    """
    Downloads a single YouTube video as MP3 and returns metadata.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOADS_DIR}/%(title)s.%(ext)s",
        "noplaylist": True,   # <-- prevent playlists
        "playlist_items": "1",  # <-- in case a playlist URL slips through
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        # If it's a playlist, yt-dlp may still return a dict with 'entries'
        if "entries" in info:
            info = info["entries"][0]  # pick first entry
        return info


def get_output_file(info: dict) -> str:
    """
    Builds the path to the downloaded MP3 file.
    """
    title = info["title"]
    return os.path.join(DOWNLOADS_DIR, f"{title}.mp3")
