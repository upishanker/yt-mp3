import re
import requests
import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from typing import Optional, Dict

def tag_mp3(file_path: str, info: dict):
    """
    Adds metadata (title, artist, album, cover art) to the MP3 file.
    """
    try:
        audio = EasyID3(file_path)
    except Exception:
    # If no ID3 tag exists, create one
        audio = EasyID3()
        audio.save(file_path)

    audio["title"] = info.get("title", "")
    audio["artist"] = info.get("uploader", "")
    audio["album"] = info.get("album", "")
    audio.save(file_path)

    # Add cover art if available
    if "thumbnail" in info and info["thumbnail"]:
        try:
            # Check if thumbnail is a local file path or URL
            if os.path.exists(info["thumbnail"]):
                # Local file
                with open(info["thumbnail"], "rb") as img_file:
                    img_data = img_file.read()
            else:
                # URL
                img_data = requests.get(info["thumbnail"]).content

            audio = ID3(file_path)
            audio.add(APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=img_data
            ))
            audio.save(file_path)
        except Exception as e:
            print(f"Warning: Could not add cover art ({e})")

def extract_artist_from_title(title: str, uploader: str) -> Dict[str, str]:
    """
    Extract artist and song name from video title using various patterns
    """
    # Common patterns for music videos
    patterns = [
        r'^(.+?)\s*[-–—]\s*(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',  # Artist - Song
        r'^(.+?)\s*:\s*(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',      # Artist: Song
        r'^(.+?)\s+by\s+(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',     # Song by Artist
        r'^(.+?)\s*\|\s*(.+?)(?:\s*\(.*\))?(?:\s*\[.*\])?$',     # Artist | Song
    ]

    # Clean title (remove common suffixes)
    clean_title = re.sub(r'\s*\((official|music|lyric|audio).*?\)', '', title, flags=re.IGNORECASE)
    clean_title = re.sub(r'\s*\[(official|music|lyric|audio).*?\]', '', clean_title, flags=re.IGNORECASE)

    for pattern in patterns:
        match = re.match(pattern, clean_title, re.IGNORECASE)
        if match:
            part1, part2 = match.groups()

            # Determine which part is likely the artist
            # Usually the first part in "Artist - Song" format
            if ' - ' in clean_title or ': ' in clean_title or ' | ' in clean_title:
                artist, song = part1.strip(), part2.strip()
            elif ' by ' in clean_title.lower():
                song, artist = part1.strip(), part2.strip()
            else:
                artist, song = part1.strip(), part2.strip()

            return {
                'artist': artist,
                'title': song,
                'confidence': 'high'
            }

    # If no pattern matches, try to detect if uploader might be the artist
    # Check if uploader name appears in title
    if uploader.lower() in title.lower():
        return {
            'artist': uploader,
            'title': title,
            'confidence': 'medium'
        }

    # Last resort: use uploader as artist
    return {
        'artist': uploader,
        'title': title,
        'confidence': 'low'
    }

def search_musicbrainz(artist: str, title: str) -> Optional[Dict[str, str]]:
    """
    Search MusicBrainz for accurate artist and song information
    """
    try:
        # MusicBrainz search API
        url = "https://musicbrainz.org/ws/2/recording"
        params = {
            'query': f'artist:"{artist}" AND recording:"{title}"',
            'fmt': 'json',
            'limit': 1
        }

        headers = {
            'User-Agent': 'YouTubeMP3Converter/1.0 (your-email@example.com)'
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('recordings'):
                recording = data['recordings'][0]
                if recording.get('artist-credit'):
                    mb_artist = recording['artist-credit'][0]['artist']['name']
                    mb_title = recording['title']
                    mb_album = None

                    # Get album info if available
                    if recording.get('releases'):
                        mb_album = recording['releases'][0]['title']

                    return {
                        'artist': mb_artist,
                        'title': mb_title,
                        'album': mb_album,
                        'source': 'musicbrainz'
                    }
    except Exception as e:
        print(f"MusicBrainz lookup failed: {e}")

    return None

def get_enhanced_metadata(info: dict) -> dict:
    """
    Get enhanced metadata with better artist detection
    """
    title = info.get('title', '')
    uploader = info.get('uploader', '')

    # First, try to parse the title
    parsed = extract_artist_from_title(title, uploader)

    # If we have high confidence, try MusicBrainz lookup
    if parsed['confidence'] == 'high':
        mb_result = search_musicbrainz(parsed['artist'], parsed['title'])
        if mb_result:
            return {
                'title': mb_result['title'],
                'artist': mb_result['artist'],
                'album': mb_result.get('album', ''),
                'thumbnail': info.get('thumbnail', ''),
                'source': 'musicbrainz'
            }

    # Return parsed result
    return {
        'title': parsed['title'],
        'artist': parsed['artist'],
        'album': info.get('album', ''),
        'thumbnail': info.get('thumbnail', ''),
        'source': 'parsed',
        'confidence': parsed['confidence']
    }