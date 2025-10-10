# Maestro's Music Manager

This is a music manager I made that fits with how I store music on my filesystem. It does not have any other advantages over common music managers.

This project may be revamped or massively altered at any time. If you wish to use it for yourself and want it to be stable, I suggest making a fork. Otherwise, feel free to use my setup!

## Key Features

> **`player.py`**
> 
> A simple terminal-based music player using Python.

> **`download/yt_downloader.py`**
> 
> A tool to download music en-masse given a list of URLs (song or playlist URLs). It does not work on DRM protected sources.

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