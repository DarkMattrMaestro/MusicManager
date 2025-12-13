import os
import subprocess
import sys
import json
import ffmpeg

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
RAW_DOWNLOAD_DIR = get_relative_path('song_library\\downloaded-raw\\')
LOCAL_DIR = get_relative_path('song_library\\local\\')
SONG_JSON_PATH = get_relative_path('songs.json')
##########################

AUDIO_EXTENSION = 'mp3'

loaded_songs = None



def load_songs():
    global loaded_songs
    with open(SONG_JSON_PATH, mode="r", encoding="utf-8") as read_file:
        loaded_songs = json.load(read_file)



def verify_local_song(s_title: str, s_author: str, directory: str, logging: bool) -> int:
    """Verify that the song file exists locally"""
    already_exists: bool = False
    if os.path.exists(os.path.join(directory, s_author)):
        for found in os.listdir(os.path.join(directory, s_author)):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path. os.path.basename(os.path.join(directory, s_author, s_title)):
                already_exists = True
        if already_exists:
            if logging: print("\033[32mLocal song file found.\033[0m")
            return 0
    
    if logging: print(f"\033[31mError: Local song file not found at `{os.path.join(directory, s_author, s_title)}.*`.\033[0m")
    return -1



def get_song_extension(s_title: str, s_author: str, directory: str) -> str:
    if os.path.exists(os.path.join(directory, s_author)):
        for found in os.listdir(os.path.join(directory, s_author)):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path. os.path.basename(os.path.join(directory, s_author, s_title)):
                return os.path.splitext(found)[1]
    
    return None



def get_song_path(s_title: str, s_author: str, directory: str) -> str:
    if os.path.exists(os.path.join(directory, s_author)):
        for found in os.listdir(os.path.join(directory, s_author)):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path. os.path.basename(os.path.join(directory, s_author, s_title)):
                return os.path.join(directory, s_author, found)
    
    return None



def modify_copy_raw_download(song, s_title: str, s_author: str) -> int:
    try:
        print(get_song_path(s_title, s_author, RAW_DOWNLOAD_DIR))
        in_path = get_song_path(s_title, s_author, RAW_DOWNLOAD_DIR)
        if in_path == None: raise FileNotFoundError()
        out_path = os.path.join(DOWNLOAD_DIR, s_author, f"{s_title}{get_song_extension(s_title, s_author, RAW_DOWNLOAD_DIR)}")
        os.makedirs(os.path.join(DOWNLOAD_DIR, s_author), exist_ok=True)
        
        if "Modifiers" in song and len(song["Modifiers"]) > 0 and isinstance(song["Modifiers"], dict):
            input_kwargs = {}
            if "Start" in song["Modifiers"]:
                try:
                    # offset: int = int(song["Modifiers"]["Start"])
                    input_kwargs["ss"] = str(song["Modifiers"]["Start"])
                except:
                    print("\033[31mError: Invalid `Start` modifier!\033[0m")
            if "End" in song["Modifiers"]:
                try:
                    # offset: int = int(song["Modifiers"]["End"])
                    input_kwargs["-to"] = str(song["Modifiers"]["Start"])
                except:
                    print("\033[31mError: Invalid `End` modifier!\033[0m")
                    
            stream = ffmpeg.input(in_path, **input_kwargs)
            
            if "Mute" in song["Modifiers"]:
                if not isinstance(song["Modifiers"]["Mute"], list):
                    song["Modifiers"]["Mute"] = [song["Modifiers"]["Mute"]]
                
                for mute_modifier in song["Modifiers"]["Mute"]:
                    try:
                        cutoffL = float(mute_modifier["CutoffL"])
                        cutoffR = float(mute_modifier["CutoffR"])
                        falloff = float(mute_modifier["Falloff"])
                        stream = ffmpeg.filter(stream, "afade", **{'enable': f'between(t,{cutoffL-falloff},{cutoffL})', 'type': 'out', 'st': cutoffL-falloff, 'duration': falloff})
                        stream = ffmpeg.filter(stream, "volume", **{'enable': f'between(t,{cutoffL},{cutoffR})'}, **{'volume': 0})
                        stream = ffmpeg.filter(stream, "afade", **{'enable': f'between(t,{cutoffR},{cutoffR+falloff})', 'type': 'in', 'st': cutoffR, 'duration': falloff})
                    except:
                        print("\033[31mError: Invalid `Mute` modifier!\033[0m")
            
            stream = ffmpeg.output(stream, out_path)
            ffmpeg.run(stream)
        else:
            ffmpeg.input(in_path).output(out_path).run()
    except FileNotFoundError as e:
        print(f"An error occurred: {e}")
        return -1
    except ffmpeg.Error as e:
        print(f"An error occurred: {e}")
        return -1
    else:
        return 0



def download_audio():
    global loaded_songs
    
    if not os.path.exists(os.path.join(SONG_JSON_PATH)):
        print(f"\033[31mError: Song JSON does not exist at `{os.path.join(SONG_JSON_PATH)}`!\033[0m")
        return
    
    load_songs()
    
    success: list[int] = []
    
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
        
        if verify_local_song(s_title, s_author, RAW_DOWNLOAD_DIR, False) >= 0 and verify_local_song(s_title, s_author, DOWNLOAD_DIR, False) < 0:
            # Raw song downloaded already
            print("\033[33mRaw song already downloaded, applying modifiers and copying.\033[0m")
            success.append(2 if modify_copy_raw_download(song, s_title, s_author) == 0 else -1)
        elif "URLs" not in song or len("".join(song["URLs"])) < 1 or not isinstance(song["URLs"], list):
            print("\033[33mNo valid `URLs` provided in JSON, assuming local file.\033[0m")
            success.append(verify_local_song(s_title, s_author, LOCAL_DIR, True))
            continue
        else:
            if verify_local_song(s_title, s_author, RAW_DOWNLOAD_DIR, False) >= 0:
                print("\033[33mThe song has already been downloaded, no download is required.\033[0m")
                success.append(1)
                continue
            
            downloaded: bool = False
            for url in song["URLs"]:
                print(f"Attempting download from `{url}`...")
                    
                ydl_opts = {
                    'verbose': True,
                    'format': f'{AUDIO_EXTENSION}/bestaudio/best',
                    'outtmpl': os.path.join(RAW_DOWNLOAD_DIR, s_author, s_title) + '.%(ext)s',
                    'restrictfilenames': True,
                    'postprocessors': [{ # Extract audio using ffmpeg
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': AUDIO_EXTENSION,
                    }]
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        error_code = ydl.download(url)
                    except:
                        print(f"\033[33mFailed to download from `{url}`.\033[0m")
                    else:
                        print(f"\032[31mDownloaded the song from `{url}`.\033[0m")
                        success.append(modify_copy_raw_download(song, s_title, s_author))
                        downloaded = True
                        break
            if not downloaded:
                print(f"\033[31mSong failed to download from the provided URLs.\033[0m")
                success.append(-1)
    
    print("\nDownload Results:")
    for i in range(len(loaded_songs)):
        colour_code = ""
        if success[i] == -1:
            colour_code = "\033[31m"
        elif success[i] == 0:
            colour_code = "\033[32m"
        elif success[i] == 1:
            colour_code = "\033[33m"
        elif success[i] == 2:
            colour_code = "\033[34m"
        print(" " + colour_code + str(loaded_songs[i].get("Title", "_")) + "   -   " + str(loaded_songs[i].get("Author", "_")) + "\033[0m")



def main():
    print("Downloading...\n")
    download_audio()
    print("\nDONE")



if __name__ == '__main__':
    main()