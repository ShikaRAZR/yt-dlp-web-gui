# yt-dlp-web-gui
Web GUI interface for yt-dlp to download videos, audio, images

## Features
- Download Audio
- Download Video (Youtube)
- Download Thumbnail (Only Youtube)
- Batch Download (Music, Video, Thumbnail)
    - Numbering (Custom Prefix)
    - Range of videos in a playlist
- Configs (Appears after sending link)
    - Remux (less options) or  Re-encode
        - Video Codec
        - Audio Codec
        - Video Quality
        - Audio Quality
        - Container (Music)
        - Container (Video)
    - Default
        - best quality codecs in mkv, mka container
    - Download Path
- Update yt-dlp
- Exit

## Might work on supporting
- Twitter, Instagram, Twitch
- Youtube community posts

## Modules
ffmpeg
yt-dlp
streamlit or nicegui