# Personal Notes
My personal notes about what I've learned while coding this project

## Links & References
https://github.com/imageio/imageio-ffmpeg <br>
https://github.com/yt-dlp/yt-dlp/tree/master <br>


Streamlit Documentation https://docs.streamlit.io/develop/api-reference <br>
Streamlet to exe file (blog) https://ploomber.io/blog/streamlit_exe/ <br>

Sets first column as index column "st.dataframe(df.set_index(df.columns[0]))" <br>
https://discuss.streamlit.io/t/hide-row-indices-when-displaying-a-dataframe-in-streamlit-v1-16-0/35296  <br>

You can use these icons in streamlit segmented control input: https://fonts.google.com/icons <br>



## FFMPEG Explained:
```
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
```


## Testing

Song Wiblotu - DYSFUNCTIONAL
```
yt-dlp -F https://youtu.be/ezOCrcKukEE
```
Video And They Shall Know No Fear | Secret Level EP: 05 | Warhammer 40K
```
yt-dlp -F https://youtu.be/4qE3q3tgSPI
```

> Test:
```
python --version
```
> Make Virtual Environment:
```
python -m venv venv
```
> Activate Virtual Environment:

```
source venv/bin/activate 
```
```
venv\Scripts\Activate.ps1
```

> run streamlit:
```
streamlit run main.py
```
>pyinstaller:
- Reference: https://ploomber.io/blog/streamlit_exe/
1. create a run.py that wraps the main() in main.py 
    - code inside:
        ```
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
                resolve_path("main.py"),
                "--global.developmentMode=false",
            ]
            sys.exit(stcli.main())

        ```
2. Create a hooks file in hooks folder (./hooks/hook-streamlit.py)
    - code inside:
        ```
        from PyInstaller.utils.hooks import copy_metadata

        datas = copy_metadata("streamlit")
        ```
3. Build with pyinstaller
    1. Build
        ```
        pyinstaller --onefile --additional-hooks-dir=./hooks run.py --clean
        ```
    2. Edit Spec file:
        - Add from ... import...
        ```
        from PyInstaller.utils.hooks import collect_all
        ```
        - making array for datas, binaries, hidden imports, including main.py
        ```
        datas = []
        binaries = []
        hiddenimports = []

        datas.append(("main.py", "."))
        
        for pkg in ["streamlit", "yt_dlp", "imageio_ffmpeg", "pandas"]:
            d, b, h = collect_all(pkg)
            datas += d
            binaries += b
            hiddenimports += h
        ```
        - replace the 3 fields in the anaysis block 
        ```
        a = Analysis(
            ['run.py'],
            pathex=[],
            binaries=binaries,
            datas=datas,
            hiddenimports=hiddenimports,
            ...
        )
        ```
    3. Build using spec file
        ```
        pyinstaller run.spec --clean
        ```




