# yt-dlp-web-gui
Web GUI interface for yt-dlp to download videos, audio, images

## Features
- Download Audio
- Download Video (Youtube)
- Download with Remux (Audio)
    - format ID for audio codex
    - custom container
- Download with Remux (Video)
    - format ID for video codec
    - format ID for audio codex
    - custom container
- Re-encode (Video)
    - Video Codec
    - Audio Codec
    - Resolution
    - Container
- Re-encode (Audio)
    - Audio Codec
    - Container
- Download Thumbnail (Only Youtube)
- Batch Download (Music, Video, Thumbnail)
    - Numbering (Custom Prefix)
    - Range of videos in a playlist
    - Default
        - best quality codecs in mkv, mka container
- Other
    - Twitter
- Exit


## Side Features
- Update yt-dlp
- Change Download Path
- Cancel Download
- Cookies From: brave, chrome, chromium, edge, firefox, opera, safari, vivaldi, whale


## Might work on supporting
- Twitter, Instagram, Twitch, Reddit
- Youtube community posts


## Features to Work On
- ~~cancel download~~
- Personal Download location (config)
- ask for cookies (cookies dont work for chromium and video error downloading with cookies activated)
- ~~ffmpeg not installed (other-twitter)~~

## Modules
ffmpeg
yt-dlp
streamlit
