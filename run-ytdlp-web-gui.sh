#!/bin/bash
# Requirements: konsole, python, uv
konsole --noclose -e bash -c "uv run --with streamlit --with yt-dlp --with imageio-ffmpeg --with pandas streamlit run main.py"
