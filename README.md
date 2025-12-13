# Maestro's Music Manager

> [!Note]
> The Python scripts automatically install the libraries upon which they depend. See the top few lines of code to see the libraries that are installed on run.

This is a music manager I made that fits with how I store music on my filesystem. It does not have any other advantages over common music managers.

This project may be revamped or massively altered at any time. If you wish to use it for yourself and want it to be stable, I suggest making a fork. Otherwise, feel free to use my setup!

## Key Features

> **`player.py`**
> 
> A simple terminal-based music player using Python.

> **`general_downloader.py`**
> 
> A tool to download music en-masse given a list of songs defined in `songs.json`. It does not work on DRM protected sources.
> To use it, simply add an entry with the author and title (use file-system-friendly characters), backup source URLs, and any of a set few pre-defined modifiers, then run the python script. For example:
> ```json
> [
>     {
>         "Title": "Tubular Bells (part one)",
>         "Author": "Mike Oldfield",
>         "URLs": ["https://www.youtube.com/watch?v=ZJkNsWCay4c"],
>         "Modifiers": {}
>     }
> ]
> ```

## Folder Structure

```
Root folder
├─{playlist/author name}
│ ├─{playlist/author name}
│ │ └─...
│ └─{song}
│
├─discs
│ └─{disc name}
│   └─{song}
│
├─song-library
│ ├─downloaded
│ │ └─{author}
│ │   └─{song}.{format}
│ ├─downloaded-raw
│ │ └─{author}
│ │   └─{song}.{format}
│ └─local
│
├─general_downloader.py
├─player.py
└─songs.json
```
