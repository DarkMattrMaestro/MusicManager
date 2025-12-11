import os
import subprocess
import sys
import json

import ctypes

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

try:
    import yt_dlp
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'yt-dlp'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'yt-dlp'])
    # import yt_dlp

def get_relative_path(path: str) -> str:
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, path)

##### Relative Paths #####
DOWNLOAD_DIR = get_relative_path('song_library\\downloaded\\')
LOCAL_DIR = get_relative_path('song_library\\local\\')
SONG_JSON_PATH = get_relative_path('songs.json')
##########################

AUDIO_EXTENSION = 'mp3'

loaded_songs = None

def load_songs():
    global loaded_songs
    with open(SONG_JSON_PATH, mode="r", encoding="utf-8") as read_file:
        loaded_songs = json.load(read_file)

def verify_local_song(s_title: str, s_author: str) -> int:
    # Verify that the file exists locally
    already_exists: bool = False
    if os.path.exists(os.path.join(LOCAL_DIR, s_author)):
        for found in os.listdir(os.path.join(LOCAL_DIR, s_author)):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path.basename(os.path.join(LOCAL_DIR, s_author, s_title)):
                already_exists = True
        if already_exists:
            print("\033[32mLocal song file found.\033[0m")
            return 0
    
    print(f"\033[31mError: Local song file not found at `{os.path.join(LOCAL_DIR, s_author, s_title)}.*`.\033[0m")
    return -1

def download_audio():
    global loaded_songs
    # is_playlist = False
    # is_music = False
    # with yt_dlp.YoutubeDL({}) as ydl:
    #     info = ydl.extract_info(url, download=False)
    #     if info.
    
    success: list[int] = []
    print(DOWNLOAD_DIR)
    
    load_songs()
    
    for song in loaded_songs:
        print("\n", song)
        
        if "Title" not in song:
            print("\033[31mError: Song JSON malformed, no `Title` provided!\033[0m")
            continue
        s_title = song["Title"]
        if "Author" not in song:
            print("\033[31mError: Song JSON malformed, no `Author` provided!\033[0m")
            continue
        s_author = song["Author"]
        
        if "URLs" not in song or len("".join(song["URLs"])) < 1 or not isinstance(song["URLs"], list):
            print("\033[33mNo valid `URLs` provided in JSON, assuming local file.\033[0m")
            success.append(verify_local_song(s_title, s_author))
            continue
        # else:
            
        #         already_exists: bool = False
        #         if os.path.exists(f'{output_dir}\\{author}'):
        #             for found in os.listdir(f'{output_dir}\\{author}'):
        #                 if '.'.join(found.split('.')[0:-1]) == song:
        #                     success.append(1)
        #                     already_exists = True
        #             if already_exists:
        #                 continue
                    
        #         ydl_opts = {
        #             'format': f'{AUDIO_EXTENSION}/bestaudio/best',
        #             'outtmpl': f'{output_dir}\\{author}\\{song}' + '.%(ext)s',
        #             'restrictfilenames': True,
        #             'postprocessors': [{ # Extract audio using ffmpeg
        #                 'key': 'FFmpegExtractAudio',
        #                 'preferredcodec': AUDIO_EXTENSION,
        #             }],
        #         }
        #     # elif not isinstance(song_ref, list):
        #     #     url = song_ref
        #     #     ydl_opts = {
        #     #         'format': f'{AUDIO_EXTENSION}/bestaudio/best',
        #     #         'outtmpl': output_dir + '\\%(playlist|)s\\%(title)s.%(ext)s',
        #     #         'restrictfilenames': True,
        #     #         'postprocessors': [{ # Extract audio using ffmpeg
        #     #             'key': 'FFmpegExtractAudio',
        #     #             'preferredcodec': AUDIO_EXTENSION,
        #     #         }],
        #     #     }
        #     else:
        #         print("Song reference " + song_ref.__str__() + " is malformed.")
        #         continue

        #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #         try:
        #             error_code = ydl.download(url)
        #         except:
        #             print(f"Failed to download {song_ref}")
        #             success.append(-1)
        #         else:
        #             success.append(0)
    
    print("\nDownload Results:")
    for i in range(len(loaded_songs)):
        colour_code = ""
        if success[i] == -1:
            colour_code = "\033[31m"
        elif success[i] == 0:
            colour_code = "\033[32m"
        elif success[i] == 1:
            colour_code = "\033[33m"
        print(" " + colour_code + str(loaded_songs[i]) + "\033[0m")



def main():
    print("Downloading...\n")
    download_audio()
    print("\nDONE")



if __name__ == '__main__':
    main()