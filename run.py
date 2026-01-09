import streamlit
import streamlit.web.cli as stcli
import os, sys


def resource_path(relative_path):
    # _MEIPASS is the temp folder PyInstaller uses for bundled files
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resource_path("main.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
