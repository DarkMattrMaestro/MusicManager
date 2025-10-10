# Maestro's Music Manager

> [!Note]
> The Python scripts automatically install the libraries upon which they depend. See the top few lines of code to see the libraries that are installed on run.

This is a music manager I made that fits with how I store music on my filesystem. It does not have any other advantages over common music managers.

This project may be revamped or massively altered at any time. If you wish to use it for yourself and want it to be stable, I suggest making a fork. Otherwise, feel free to use my setup!

## Key Features

> **`player.py`**
> 
> A simple terminal-based music player using Python.

> **`download/yt_downloader.py`**
> 
> A tool to download music en-masse given a list of URLs (song or playlist URLs). It does not work on DRM protected sources.
> To use it, simply add your source URLs in the URLS list, then run the python script. For example:
> ```
> URLS = [
>     "https://www.youtube.com/@artism6843/videos"
> ]
> ```

## Folder Structure

```
Root folder
├─{playlist/author name}
│ ├─{playlist/author name}
│ │ └─...
│ └─{song}
├─{song}
├─download
│ ├─yt_downloader.py
│ ├─{song downloaded by `yt_downloader.py`}
│ └─{playlist downloaded by `yt_downloader.py`}
│   └─{song downloaded by `yt_downloader.py`}
└─player.py
```
