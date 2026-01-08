import streamlit as st
import yt_dlp
from yt_dlp import YoutubeDL
import imageio_ffmpeg as ffmpeg
import importlib.metadata
import pandas as pd

# Web GUI yt-dlp
def main():
    view_code_test_expander()
    view_tutorial_expander()

    st.write("## Video Downloader")
    version = importlib.metadata.version("yt-dlp")
    print("yt-dlp version:", version)
    st.write("yt-dlp version:", version)
    st.write("---")

    # Options for download mode
    encoding_config_map = {
        0: "Default",
        1: "Remux",
        2: "Re-encode",
        3: "Batch(Default)"
    }
    encoding_config_selection = st.segmented_control(
        "Encoding Setting",
        options=encoding_config_map.keys(),
        format_func=lambda option: encoding_config_map[option],
        selection_mode="single",
        default=0
    )
    # Options for the type of media you want to download
    media_config_map = {
        0: "Download Audio",
        1: "Download Video",
        2: "Download Thumbnail",
    }
    media_config_option = st.selectbox(
        "Choose Media Type:",
        options=media_config_map.keys(),
        format_func=lambda option: media_config_map[option],
    )
    # user inputs url
    url_input = st.text_input("Input URL")

    # Test
    st.write("Encoding: ", encoding_config_selection)
    st.write("Media: ", media_config_option)

    # Button to continue or download
    button_name = ""
    if(encoding_config_selection==0):
        button_name = "Download"
    if(encoding_config_selection==1):
        button_name = "Continue"

    if (button_name != ""):
        if st.button(button_name):
            url_download_config(url_input, encoding_config_selection, media_config_option)
        


def url_download_config(url_input, encoding_config_selection, media_config_option):
    # Depending on user input downloads default audio and video files or gives more options when remux/re-encode/batch are chosen
    st.write("---")
    with st.spinner("Processing..."):
        is_valid = is_supported_by_ytdlp(url_input)
    
    color = "red"
    if (is_valid):
        color = "green"
    st.write("URL Valid? ", url_input)
    st.badge(str(is_valid), color=color)
    
    with st.spinner("Processing..."):
        # Default
        if (is_valid and encoding_config_selection==0):
            if(media_config_option==0):
                download_media(url_input, ydl_opts_best_audio_mka())
                st.success("Audio (Default) Downloaded!")
    
            if (media_config_option==1):
                download_media(url_input, ydl_opts_best_video_mkv())
                st.success("Video (Default) Downloaded!")

            if (media_config_option==2):
                download_media(url_input, ydl_opts_thumbnail())
                st.success("Thumbnail (Default) Downloaded!")
        
        # Remux
        if (is_valid and encoding_config_selection==1):
            if(media_config_option==0):
                download_media_remux(url_input)
            

# Helpers with user input
def download_media_remux(url):
    view_media_codec_list(url)



# Helpers
def is_supported_by_ytdlp(url: str) -> bool:
    # Check if yt-dlp supports the URL
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            ydl.extract_info(url, download=False)
        return True
    except yt_dlp.utils.DownloadError:
        return False

def download_media(url, ydl_opts):
    # download youtube media with configs
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

def ydl_opts_best_audio_mka():
    # Python dictionary config for default youtube audio download
    output = {
        "format": "bestaudio/best",                 # Download best quality (audio)
        "outtmpl": "%(title).80s.mka",              # File name and extension
        "noplaylist": True,                         # Only download single video
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(), # custom ffmpeg location
        # 'postprocessors': [{
            # 'key': 'FFmpegExtractAudio',
            # 'preferredcodec': 'opus',   # Prefer Opus (doesnt work sometimes)
        # }],
        "quiet": False,                             # Show progress
        "progress_hooks": [
            lambda d: print(f"{d['_percent_str']} {d['_eta_str']} remaining") if d['status'] == 'downloading' else None
        ]
    }
    return output

def ydl_opts_best_video_mkv():
    # Python dictionary config for default youtube video download
    output = {
        "format": "bestvideo+bestaudio/best",       # Download best quality (video + audio)
        "outtmpl": "%(title).80s.%(ext)s",          # File name and extension
        "noplaylist": True,                         # Only download single video
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(), # custom ffmpeg location
        "merge_output_format": "mkv",               # Container format
        "quiet": False,                             # Show progress
        "progress_hooks": [
            lambda d: print(f"{d['_percent_str']} {d['_eta_str']} remaining") if d['status'] == 'downloading' else None
        ]
    }
    return output

def ydl_opts_thumbnail():
    # Python dictionary config for default youtube thumbnail download
    output = {
        "skip_download": True,                      # Don't download the video
        "writethumbnail": True,                     # Download thumbnail
        "outtmpl": "%(title).80s.%(ext)s",          # File name and extension
        "noplaylist": True,                         # Only download single video
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(), # custom ffmpeg location
        "quiet": False,                             # Show progress
        "progress_hooks": [
            lambda d: print(f"{d['_percent_str']} {d['_eta_str']} remaining") if d['status'] == 'downloading' else None
        ]
    }
    return output



# Display Helpers
def view_media_codec_list(url):
    # Displays a table of available video/audio codecs of a youtube url and returns the table
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)  # download=False like -F similar to calling "yt-dlp -F [url]"
        formats = info.get("formats", [])
        data_list = pd.DataFrame([{
            "format_id": f['format_id'],
            "ext": f['ext'],
            "height": f.get('resolution'),
            "fps": f.get('fps'),
            "vcodec": f['vcodec'],
            "acodec": f['acodec'],
        } for f in formats])
        st.subheader("Available Formats")
        st.table(data_list.set_index(data_list.columns[0])) # Sets first column as index column
        st.success("Info Obtained")
        return data_list

def view_code_test_expander():
    # Test
    with st.expander("Code Testing"):
        st.write("\nSong")
        st.write("https://youtu.be/ezOCrcKukEE")
        st.code("https://youtu.be/ezOCrcKukEE")
        st.code("yt-dlp -F https://youtu.be/ezOCrcKukEE")
        st.write("\nVideo")
        st.write("https://youtu.be/4qE3q3tgSPI")
        st.code("https://youtu.be/4qE3q3tgSPI")
        st.code("yt-dlp -F https://youtu.be/4qE3q3tgSPI")


def view_tutorial_expander():
    # General info and tips on how to use this program and what to expect
    with st.expander("Tutorial & Guide"):
        st.write("Encode Setting (Default) will use a .mka container for audio and a .mkv container for videos, while choosing the highest bitrate/resolution quality")
        st.write("Encode Setting (Remux) will allow you to choose specific video and audio codecs provided by youtube, as well as a container of your choosing, some audio/video codecs are seperate while some are combined, you can mix and match")
        st.write("Encode Setting (Re-encode) will download the highest quality audio and video and reencode to an audio/video codec and container of your choosing")
        st.write("Encode Setting (Batch) Download youtube playlists with Default setting")
        st.write("#### Note:")
        st.write("Only certain codecs are provided by youtube and re-encoding may be required if you want certain ones, re-encoding WILL lower quality of video")
        st.write("Try to maintain quality by remuxing instead of re-encoding, using existing audio/video codecs youtube provides with whatever container is compatible")
        st.write("Certain codecs and containers are not compatible with each other, any audio/video codecs can be merged as long as the container is compatible with both")
        st.write("#### Common Codecs Youtube uses")
        video_codec_table = pd.DataFrame(
            {
                "Video Codec": ["avc1(H.264)", "vp09(VP9)", "av01(AV1)"],
            },
            index=["≤1080p","(Maybe 1080p), 1440p–8K","New devices/experimental"],
        )
        st.table(video_codec_table)
        audio_codec_container_table = pd.DataFrame(
            {
                "Audio Codec": ["mp4a (AAC)","opus","ac-3 (Audio Coding 3)", "ec-3 (Enhanced AC-3/E-AC-3)"],
                "Container Codec": ["m4a (audio only)","webm","mp4",""]
            }
        )
        st.table(audio_codec_container_table.set_index(audio_codec_container_table.columns[0])) # Sets first column as index column
        
        


if __name__ == "__main__":
    main()



def notes():
    '''
    Notes

    https://github.com/imageio/imageio-ffmpeg
    https://github.com/yt-dlp/yt-dlp/tree/master

    yt-dlp -F https://youtu.be/ezOCrcKukEE Song Wiblotu - DYSFUNCTIONAL
    yt-dlp -F https://youtu.be/4qE3q3tgSPI Video And They Shall Know No Fear | Secret Level EP: 05 | Warhammer 40K

    source venv/bin/activate





    streamlit run main.py
    https://docs.streamlit.io/develop/api-reference
    https://ploomber.io/blog/streamlit_exe/
    https://discuss.streamlit.io/t/hide-row-indices-when-displaying-a-dataframe-in-streamlit-v1-16-0/35296 # Sets first column as index column "st.dataframe(df.set_index(df.columns[0]))"
    You can use these icons in streamlit segmented control input:
    https://fonts.google.com/icons





    ffmpeg -i input.mp4 -c:v libx265 -crf 20 -preset slow -c:a copy output.mp4
    input file: -i
    video codec: -c:v
    quality (0-51, recommend 18): -crf
    process time (most setting don't affect quality): -preset
        ultrafast
        superfast
        veryfast
        faster
        fast
        medium (default)
        slow
        slower
        veryslow
    audio codec: -c:a
    '''


def useless():
    
    # panda is used instead of tabulate because i need to interact with the info
    '''
    def view_media_codec_list(url):
        ydl_opts = {}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # download=False like -F
            formats = info.get("formats", [])
            table = []
            for f in formats:
                table.append([
                    f['format_id'],
                    f['ext'],
                    f.get('height') or "-",
                    f.get('fps') or "-",
                    f['vcodec'],
                    f['acodec'],
                ])
        for f in formats:
            st.write(tabulate(table, headers=["format_id", "ext", "height", "fps", "vcodec", "acodec"]))
    '''
