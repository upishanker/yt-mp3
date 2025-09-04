import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC


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
