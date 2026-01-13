import streamlit as st
import yt_dlp
from yt_dlp import YoutubeDL
import imageio_ffmpeg as ffmpeg
import importlib.metadata
import pandas as pd
from pathlib import Path

import subprocess
import sys

# Global variables
download_directory = Path.home()  / "Downloads"
cookies = None

# Simple progress bar
progress_bar = st.progress(0)

# Check if ytdlp download progress should be canceled
cancel_flag = False

# Web GUI yt-dlp
def main():
    view_tutorial_expander()

    st.write("## Media Downloader (Beta)")
    version = importlib.metadata.version("yt-dlp")

    # yt-dlp 
    column1, column2 = st.columns([.4,1], vertical_alignment="center")
    with column1:
        st.write("yt-dlp version:", version)
    with column2:
        if st.button("Update", key="update_button"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
    st.write("Download Directory:", download_directory)
    st.write("---")

    # Test
    print("yt-dlp version:", version)
    print("Current directory of file:", Path.cwd())

    # Option to use cookies
    on = st.toggle("Cookies from Browser?")
    global cookies
    if on:
        cookies_config_option = st.selectbox(
            "Choose Browser to Use Cookie From (Recommended to use throwaway account):",
            ("chrome","chromium","firefox","brave","edge","opera","safari","vivaldi","whale",)
        )
        cookies = (cookies_config_option, )
    else:
        cookies = None


    # Options for download mode
    encoding_config_list = {
        0: "Default",
        1: "Remux(NoCookies)",
        2: "Re-encode",
        3: "Thumbnail",
        4: "Batch(Default)",
        5: "Other"
    }
    encoding_config_selection = st.segmented_control(
        "Encoding Setting",
        options=encoding_config_list.keys(),
        format_func=lambda option: encoding_config_list[option],
        selection_mode="single",
        default=0
    )

    # Options for the type of media you want to download
    media_config_list = {}
    if (encoding_config_selection==0 or encoding_config_selection==1 or encoding_config_selection==2):
        media_config_list = {
            0: "Audio",
            1: "Video",
        }
    if (encoding_config_selection==3):
        media_config_list = {
            0: "Youtube Thumbnail"
        }
    if (encoding_config_selection==4):
        media_config_list = {
            0: "Audio",
            1: "Video",
            2: "Youtube Thumbnail"
        }
    if (encoding_config_selection==5):
        media_config_list = {
            0: "Twitter (Video)"
        }
    media_config_option = st.selectbox(
        "Choose Media Download Type:",
        options=media_config_list.keys(),
        format_func=lambda option: media_config_list[option],
    )
    # user inputs url
    url_input = st.text_input("Input URL")

    # Test
    print("encoding_config_selection: ", encoding_config_selection)
    print("media_config_option: ", media_config_option)

    # Default, Thumbnail, Other
    if(encoding_config_selection==0 or encoding_config_selection==3 or encoding_config_selection==5):
        if st.button("Download", key="main_button"):
            url_download_config(url_input, encoding_config_selection, media_config_option)
    
    # I hate session states
    # Initialize variables that need sessions
    if 'id_data_frame_session' not in st.session_state:
        st.session_state['id_data_frame_session'] = pd.DataFrame()
    if 'id_tuple_acodec_session' not in st.session_state:
        st.session_state['id_tuple_acodec_session'] = ()
    if 'id_tuple_vcodec_session' not in st.session_state:
        st.session_state['id_tuple_vcodec_session'] = ()
    if 'input_container_for_codecs' not in st.session_state:
        st.session_state['input_container_for_codecs'] = ()
    if 'id_acodec' not in st.session_state:
        st.session_state['id_acodec'] = ""
    if 'id_vcodec' not in st.session_state:
        st.session_state['id_vcodec'] = ""
    if 'container_type' not in st.session_state:
        st.session_state['container_type'] = ""
    # Remux session state menu
    if (encoding_config_selection == 1):
        # Button to check url and make a table of formats and fine list of ids for acodecs, vcodecs and containers
        if st.button("Check URL", key="check_button"):
            with st.spinner("Processing..."):
                if (is_supported_by_ytdlp(url_input) != 1):
                    st.badge("Invalid URL for Youtube or Cookies Required", color="red")
                    return
                check_media_remux(url_input, media_config_option)
                print(st.session_state['id_tuple_acodec_session'])
                print(st.session_state['id_tuple_vcodec_session'])
        if not st.session_state['id_data_frame_session'].empty:
            st.table(st.session_state['id_data_frame_session'])
        # selectboxes for ids of acodecs, vcodecs and containers
        ids_with_acodec_box = st.selectbox(
            "Choose format_ID with an ACODEC stream to remux:",
            options=st.session_state['id_tuple_acodec_session'],
            key=("remux_acodec_box"),
        )
        st.session_state['id_acodec'] = ids_with_acodec_box
        if (media_config_option==1):
            ids_with_vcodec_box = st.selectbox(
                "Choose format_ID with a VCODEC stream to remux:",
                options=st.session_state['id_tuple_vcodec_session'],
                key=("remux_vcodec_box"),
            )
            st.session_state['id_vcodec'] = ids_with_vcodec_box
        codec_container_box = st.selectbox(
            "Choose CONTAINER compatible with selected codecs",
            options=st.session_state['input_container_for_codecs'],
            key=("remux_container_box"),
        )
        st.session_state['container_type'] = codec_container_box
        # download using configuration from check url button, then resetting states
        if st.button("Download", key="main_button"):
            url_download_config(url_input, encoding_config_selection, media_config_option)
            st.session_state['id_data_frame_session'] = pd.DataFrame()
            st.session_state['id_tuple_acodec_session'] = ()
            st.session_state['id_tuple_vcodec_session'] = ()
            st.session_state['input_container_for_codecs'] = ()
            st.session_state['id_acodec'] = ""
            st.session_state['id_vcodec'] = ""
            st.session_state['container_type'] = ""

    else:
        st.session_state['id_data_frame_session'] = pd.DataFrame()
        st.session_state['id_tuple_acodec_session'] = ()
        st.session_state['id_tuple_vcodec_session'] = ()
        st.session_state['input_container_for_codecs'] = ()
        st.session_state['id_acodec'] = ""
        st.session_state['id_vcodec'] = ""
        st.session_state['container_type'] = ""
    
        
        

# Helper With User Input
def url_download_config(url_input, encoding_config_selection, media_config_option):
    # Depending on user input downloads default audio and video files or gives more options when remux/re-encode/batch are chosen
    st.write("---")
    with st.spinner("Processing..."):
        is_valid_url = is_supported_by_ytdlp(url_input)
    
    st.write("URL: ", url_input)
    st.write("is_valid_url: ", is_valid_url)
    
    # Ends function if invalid url
    if (is_valid_url == 0):
        st.badge("Invalid URL or Cookies Required", color="red")
        return

    with st.spinner("Processing..."):
        if(is_valid_url==1):
            # 0 Default Options
            if (encoding_config_selection==0 and media_config_option==0):
                download_media(url_input, ydl_opts_best_audio_mka())
                st.success("(Default) Audio Downloaded!")
                st.write(download_directory)
            if (encoding_config_selection==0 and media_config_option==1):
                download_media(url_input, ydl_opts_best_video_audio_mkv())
                st.success("(Default) Video Downloaded!")
                st.write(download_directory)

            # 1 Remux Options
            if(encoding_config_selection==1):
                if (media_config_option==0):
                    download_media(url_input, ydl_opts_audio_remux(st.session_state['id_acodec'], st.session_state['container_type']))
                if (media_config_option==1):
                    download_media(url_input, ydl_opts_video_audio_remux(st.session_state['id_vcodec'], st.session_state['id_acodec'], st.session_state['container_type']))   

            # 3 Thumbnail Option   
            if (encoding_config_selection==3 and media_config_option==0):
                download_media(url_input, ydl_opts_thumbnail())
                st.success("Thumbnail Downloaded!")
                st.write(download_directory)
        
        # Other Options
        if (is_valid_url==2):
            if (encoding_config_selection==5 and media_config_option==0):
                view_media_codec_list(url_input)
                download_media(url_input, ydl_opts_twitter_video_audio())
                st.success("(Other) Twitter Media Downloaded!")
                st.write(download_directory)

        # Notify User Error
        if ((encoding_config_selection==0 or encoding_config_selection==1 or encoding_config_selection==2 or encoding_config_selection==3 or encoding_config_selection==4) and is_valid_url != 1):
            st.badge("Not a Youtube URL", color="red") 
        if (encoding_config_selection==5 and is_valid_url != 2):
            st.badge("Not a Twitter URL", color="red")
            

def check_media_remux(url, media_config_option):
    # data_list is a Pandas DataFrame, a type of 2 dimensional data structure with rows and columns
    data_list = view_media_codec_list(url)

    new_data = pd.DataFrame()
    for row in data_list.itertuples(index=False):
        if ((row.acodec != "none" and row.vcodec == "none") or (row.vcodec != "none" and row.acodec == "none")):
            new_data = pd.concat(
                [new_data, pd.DataFrame([row._asdict()])],
                ignore_index=True
        )
    st.session_state['id_data_frame_session'] = new_data
    #st.session_state['id_data_frame_session'] = (data_list.set_index(data_list.columns[0]))# Sets first column as index column

    # Remux Audio
    format_id_tuple_with_acodec = ()
    # Intertuples is an iterator (not an array or list but an object itself using its own methods or for loop to go through) that makes each row a tuple
    for row in data_list.itertuples(): # each row is a tuple containing format_id, acodec, vcodec and whatever we chose to add to the DataFrame for a single media
        if (row.acodec != "none" and row.vcodec == "none"): # in this case we checking if this row (media) has an acodec 
            format_id_tuple_with_acodec = format_id_tuple_with_acodec + (row.format_id,) # adding the id of the row that has an acodec but as an int instead of string for sorting
            print("id:"+row.format_id +" acodec:"+row.acodec)
    st.session_state['id_tuple_acodec_session'] = tuple(sorted(format_id_tuple_with_acodec))
    st.session_state['input_container_for_codecs'] = ("mp3", "mka", "oga", "m4a",)
    # Remux Video
    format_id_tuple_with_vcodec = ()
    for row in data_list.itertuples():
        if (row.vcodec != "none" and row.acodec == "none"):
            format_id_tuple_with_vcodec = format_id_tuple_with_vcodec + (row.format_id,)
            print("id:"+row.format_id +" vcodec:"+row.vcodec)
    st.session_state['id_tuple_vcodec_session'] = tuple(sorted(format_id_tuple_with_vcodec))
    if (media_config_option==1):
        st.session_state['input_container_for_codecs'] = ("mp4", "mkv", "webm", "ts", "avi", "mov", "ogg",)

# Helpers
def is_supported_by_ytdlp(url: str):
    # Check if yt-dlp supports the URL
    # Does not support = 0
    # Youtube = 1
    # Twitter = 2
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            ydl.extract_info(url, download=False)
        if("youtube" in url or "youtu.be" in url):
            return 1
        if("twitter" in url or "x.com" in url):
            return 2
    except yt_dlp.utils.DownloadError:
        return 0

def download_media(url, ydl_opts):
    # Button to cancel downloads
    if st.button("Cancel Download", key="cancel_button"):
        global cancel_flag
        cancel_flag = True
    # download youtube media with configs
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

# Helpers - youtube download configurations
def ydl_opts_best_audio_mka():
    # Python dictionary config for default youtube audio download
    output = {
        # "format": "bestaudio",
        "outtmpl": str(download_directory / "%(title).80s.%(ext)s"),
        "noplaylist": True,
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(),
        "quiet": False,
        "cookiesfrombrowser": cookies,
        "progress_hooks": [
             st_progress_hook,
        ]
    }
    if (cookies == None):
        output["format"] = "bestaudio"
        output["postprocessors"] = [{
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mka",
        }]
    else:
        output["format"] = "best"
        output["postprocessors"] = [{
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mka",
        }]
    return output

def ydl_opts_best_video_audio_mkv():
    # Python dictionary config for default youtube video audio download
    output = {
        # "format": "bestvideo+bestaudio",
        "outtmpl": str(download_directory / "%(title).80s.%(ext)s"),
        "noplaylist": True,
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(),
        "quiet": False,
        "cookiesfrombrowser": cookies,
        "progress_hooks": [
            st_progress_hook,
        ] # lambda d: print(f"{d['_percent_str']} {d['_eta_str']} remaining") if d['status'] == 'downloading' else None
    }
    if (cookies == None):
        output["format"] = "bestvideo+bestaudio"
        output["merge_output_format"] = "mkv"
    else:
        output["format"] = "best"
        output["postprocessors"] = [{
            "key": "FFmpegVideoRemuxer",
            "preferedformat": "mkv",
        }]
    return output

def ydl_opts_thumbnail():
    # Python dictionary config for youtube thumbnail download
    output = {
        "skip_download": True,                      # Don't download the video
        "writethumbnail": True,                     # Download thumbnail
        "outtmpl": str(download_directory / "%(title).80s.%(ext)s"),          # File name and extension
        "noplaylist": True,                         # Only download single video
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(), # custom ffmpeg location
        "quiet": False,                             # Show progress
        "cookiesfrombrowser": cookies,
        "progress_hooks": [
            st_progress_hook,
        ]
    }
    return output

def ydl_opts_audio_remux(audio_format_id, container_type):
    # Python dictionary config for remux youtube audio download
    output = {
        "format": str(audio_format_id),                 # Download best quality (audio)
        "outtmpl": str(download_directory / "%(title).80s.%(ext)s"),# File name and extension
        "postprocessors": [{
            "key": "FFmpegVideoRemuxer",
            "preferedformat": str(container_type),
        }],
        "noplaylist": True,                         # Only download single video
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(), # custom ffmpeg location
        "quiet": False,                             # Show progress
        "cookiesfrombrowser": cookies,
        "progress_hooks": [
            st_progress_hook,
        ]
    }
    return output

def ydl_opts_video_audio_remux(video_format_id, audio_format_id, container_type):
    # Python dictionary config for remux youtube video audio download
    output = {
        "format": str(video_format_id+"+"+audio_format_id),         # Download best quality (audio)
        "outtmpl": str(download_directory / "%(title).80s.%(ext)s"),# File name and extension
        "merge_output_format": str(container_type),
        "noplaylist": True,                         # Only download single video
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(), # custom ffmpeg location
        "quiet": False,                             # Show progress
        "cookiesfrombrowser": cookies,
        "progress_hooks": [
            st_progress_hook,
        ]
    }
    return output

def ydl_opts_twitter_video_audio():
    # Python dictionary config for twitter video download
    output = {
        "format": "bestvideo+bestaudio/best",       # Download best quality (video + audio)
        "outtmpl": str(download_directory / "%(uploader)s - %(id)s - %(media_id)s.%(ext)s"), # File name and extension
        "noplaylist": True,                         # Only download single video
        "ffmpeg_location": ffmpeg.get_ffmpeg_exe(), # custom ffmpeg location
        "quiet": False,                             # Show progress
        "cookiesfrombrowser": cookies,
        "progress_hooks": [
            st_progress_hook,
        ]
    }
    return output

# Display Helpers
def view_media_codec_list(url):
    # Displays a table of available video/audio codecs of a youtube url and returns the table
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        
        info = ydl.extract_info(url, download=False)  # info is a dictionary that has all metadata about the mutiple medias
        formats = info.get("formats", []) # formats is another dictionary but more specific, also having a dictionary for each media, with keys from "formats" like format_id, ext, vcodec, acodec, vbr, abr, tbr
        url_type = ""
        if ("you" in url):
            url_type = "Youtube"
            data_list = pd.DataFrame([{
                "format_id": f['format_id'], # Each Creates a New Dictionary adding to data frame, each media's data
                "ext": f['ext'],
                "resolution": f.get('resolution'), # .get is used in case key is missing so there are no errors
                "fps": f.get('fps'),
                "vcodec": f['vcodec'],
                "acodec": f['acodec'],
                "tbr": f.get('tbr'),
                "filesize_MB": (
                    round(f["filesize"] / 1024 / 1024, 2)
                    if f.get("filesize") else None
                ),
            } for f in formats]) # f is a dictionary, with keys like format_id, vcodec of only EACH media, iterating through each media

        if ("x.com" in url or "twitter" in url):
            url_type = "Twitter"
            data_list = pd.DataFrame([{
                "format_id": f['format_id'],
                "ext": f['ext'],
                "resolution": f.get('resolution'),
                "vcodec": f.get('vcodec', "unknown"),
                "acodec": f.get('acodec', "unknown"),
                "tbr": f.get('tbr'),
                "filesize_MB": (
                    round(f["filesize"] / 1024 / 1024, 2)
                    if f.get("filesize") else None
                ),
            } for f in formats])
        
        st.subheader("Available Formats")
        st.write(url_type + " URL") 
        st.success("Info Obtained")
        return data_list


def view_tutorial_expander():
    # General info and tips on how to use this program and what to expect
    with st.expander("Tutorial & Guide"):
        st.write("Encode Setting (Default) will use a .mka container for audio and a .mkv container for videos, while choosing the highest bitrate/resolution quality (with cookies on, quality and filetype might be worse or different)")
        st.write("Encode Setting (Remux) will allow you to choose specific video and audio codecs provided by youtube, as well as a container of your choosing, some audio/video codecs are seperate while some are combined, you can mix and match")
        st.write("Encode Setting (Re-encode) will download the highest quality audio and video and reencode to an audio/video codec and container of your choosing")
        st.write("Encode Setting (Batch) Download youtube playlists with Default setting")
        st.write("#### Note:")
        st.write("Only certain codecs are provided by youtube and re-encoding may be required if you want certain ones, re-encoding WILL lower quality of video")
        st.write("Try to maintain quality by remuxing instead of re-encoding, using existing audio/video codecs youtube provides with whatever container is compatible")
        st.write("Certain codecs and containers are not compatible with each other, any audio/video codecs can be merged as long as the container is compatible with both")
        st.markdown("<span style='background-color: darkred'>Some content maybe restricted and require an account, try using cookies from browser.  Recommended to use throwaway account, bannable maybe?</span>", unsafe_allow_html=True)
        st.write("With cookies ON, youtube only provides codec streams that are muxed already, no separate audio/video streams, you may not have the best quality available, remuxing option is not available")
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
                "Containers": ["m4a (audio only)","webm","mp4",""]
            }
        )
        st.table(audio_codec_container_table.set_index(audio_codec_container_table.columns[0])) # Sets first column as index column
        
def st_progress_hook(d):
    global cancel_flag
    if cancel_flag:
        raise Exception("Download canceled")
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            progress_bar.progress(downloaded / total)


if __name__ == "__main__":
    main()




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
