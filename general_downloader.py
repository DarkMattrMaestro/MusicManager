import json
import os
import subprocess
import sys
import shutil
import ffmpeg

import ctypes

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

try:
    import yt_dlp
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'yt-dlp', "-U"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'yt-dlp', "-U"])
    # import yt_dlp

###########################################################################

def get_relative_path(path: str) -> str:
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(curr_dir, path)

##### Relative Paths #####
DOWNLOAD_DIR = get_relative_path('song_library\\downloaded\\')
RAW_DOWNLOAD_DIR = get_relative_path('song_library\\downloaded-raw\\')
LOCAL_DIR = get_relative_path('song_library\\local\\')
DISCS_DIR = get_relative_path('discs')
SONG_JSON_PATH = get_relative_path('songs.json')
##########################

AUDIO_EXTENSION = 'mp3'

class SongData:
    loaded_songs = None

    def load_songs() -> bool:
        if not os.path.exists(os.path.join(SONG_JSON_PATH)):
            print(f"\033[31mError: Song JSON does not exist at `{os.path.join(SONG_JSON_PATH)}`!\033[0m")
            return False

        with open(SONG_JSON_PATH, mode="r", encoding="utf-8") as read_file:
            SongData.loaded_songs = json.load(read_file)
        
        return True



def verify_local_song(s_title: str, s_author: str, directory: str, logging: bool) -> int:
    """Verify that the song file exists locally"""
    already_exists: bool = False
    if os.path.exists(os.path.join(directory, s_author)):
        for found in os.listdir(os.path.join(directory, s_author)):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path.basename(os.path.join(directory, s_author, s_title)):
                already_exists = True
        if already_exists:
            if logging: print("\033[32mLocal song file found.\033[0m")
            return 0
    
    if logging: print(f"\033[31mError: Local song file not found at `{os.path.join(directory, s_author, s_title)}.*`.\033[0m")
    return -1



def verify_disc_song(s_title: str, s_author: str, disc: str, directory: str, logging: bool) -> int:
    """Verify that the song file exists in a disc"""
    already_exists: bool = False
    full_dir = os.path.join(directory, disc)
    if os.path.exists(full_dir):
        for found in os.listdir(full_dir):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path.basename(os.path.join(full_dir, f"{s_title} - {s_author}")):
                already_exists = True
        if already_exists:
            if logging: print("\033[32mLocal song file found.\033[0m")
            return 0
    
    if logging: print(f"\033[31mError: Local song file not found at `{os.path.join(full_dir, s_title)}.*`.\033[0m")
    return -1



def get_song_extension(s_title: str, s_author: str, directory: str) -> str:
    if os.path.exists(os.path.join(directory, s_author)):
        for found in os.listdir(os.path.join(directory, s_author)):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path.basename(os.path.join(directory, s_author, s_title)):
                return os.path.splitext(found)[1]
    
    return None



def get_song_path(s_title: str, s_author: str, directory: str) -> str:
    if os.path.exists(os.path.join(directory, s_author)):
        for found in os.listdir(os.path.join(directory, s_author)):
            if os.path.basename('.'.join(found.split('.')[0:-1])) == os.path.basename(os.path.join(directory, s_author, s_title)):
                return os.path.join(directory, s_author, found)
    
    return None

############################################################################

def modify_copy_raw_download(song, s_title: str, s_author: str) -> int:
    try:
        print(get_song_path(s_title, s_author, RAW_DOWNLOAD_DIR))
        in_path = get_song_path(s_title, s_author, RAW_DOWNLOAD_DIR)
        if in_path == None: raise FileNotFoundError()
        out_path = os.path.join(DOWNLOAD_DIR, s_author, f"{s_title}{get_song_extension(s_title, s_author, RAW_DOWNLOAD_DIR)}")
        os.makedirs(os.path.join(DOWNLOAD_DIR, s_author), exist_ok=True)
        
        stream = ffmpeg.input(in_path)
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
            
        ffmpeg.output(stream, out_path).run()
    except FileNotFoundError as e:
        print(f"An error occurred: {e}")
        return -1
    except ffmpeg.Error as e:
        print(f"An error occurred: {e}")
        return -1
    else:
        return 0



def copy_to_discs(s_title: str, s_author: str, s_discs: list[str]) -> int:
    in_path = get_song_path(s_title, s_author, DOWNLOAD_DIR)
    if in_path == None:
        print("The song file was not found when copying to discs.")
        return -1
    
    stream = ffmpeg.input(in_path)
    
    success: list[int] = []
    
    for disc in s_discs:
        if verify_disc_song(s_title, s_author, disc, DISCS_DIR, False) >= 0:
            if ArgumentParser.verbose: print(f"\033[33mThe song is already in disc \"{disc}\", no copying is required.\033[0m")
            success.append(1)
            continue
        else:
            if ArgumentParser.verbose: print(f"Copying to disc \"{disc}\".")
            disc_out_path = os.path.join(DISCS_DIR, disc, f"{s_title} - {s_author}.mp3")
            os.makedirs(os.path.join(DISCS_DIR, disc), exist_ok=True)
            if get_song_extension(s_title, s_author, DOWNLOAD_DIR) == ".mp3": # TODO: Generalize for any wanted extension
                try:
                    shutil.copy2(in_path, disc_out_path)
                except:
                    print(f"\033[31mFailed to convert and copy to {disc}\033[0m")
                    success.append(-1)
                else:
                    success.append(0)
            else:
                try:
                    ffmpeg.output(stream, disc_out_path, format='mp3').run()
                except ffmpeg.Error as e:
                    print(f"\033[31mFailed to convert and copy to {disc}\033[0m")
                    success.append(-1)
                else:
                    success.append(0)
    
    if s_discs:
        print("Targeted discs: ", end="")
        msg = []
        for i in range(len(s_discs)):
            colour_code = ""
            if success[i] == -1:
                colour_code = "\033[31m"
                num_failed += 1
            elif success[i] == 0:
                colour_code = "\033[32m"
            elif success[i] == 1:
                colour_code = "\033[33m"
            elif success[i] == 2:
                colour_code = "\033[34m"
            msg.append(f"{colour_code}{s_discs[i]}\033[0m")
        print(', '.join(msg) + ".")
    else:
        if ArgumentParser.verbose: print("No targeted discs.")



def extract_song_metadata(song) -> tuple:
    # Load s_title
    if "Title" not in song:
        print("\033[31mError: Song JSON malformed, no `Title` provided!\033[0m")
        return (False, None, None, None)
    s_title = song["Title"]
    
    # Load s_author
    if "Author" not in song:
        print("\033[31mError: Song JSON malformed, no `Author` provided!\033[0m")
        return (False, None, None, None)
    s_author = song["Author"]
    
    # Load s_discs
    s_discs = song["Discs"] if "Discs" in song else []
    
    return (True, s_title, s_author, s_discs)



def download_audio():
    if not SongData.load_songs(): return
    
    success: list[int] = []
    
    for song in SongData.loaded_songs:
        print("\n", song)
        
        # Extract song metadata
        extracted_success, s_title, s_author, s_discs = extract_song_metadata(song)
        if not extracted_success:
            success.append(-1)
            continue
        
        # Download and modify the song, as required
        if verify_local_song(s_title, s_author, RAW_DOWNLOAD_DIR, False) >= 0 and verify_local_song(s_title, s_author, DOWNLOAD_DIR, False) < 0:
            # Raw song downloaded already
            print("\033[33mRaw song already downloaded, applying modifiers and copying.\033[0m")
            success.append(2 if modify_copy_raw_download(song, s_title, s_author) == 0 else -1)
        elif "URLs" not in song or len("".join(song["URLs"])) < 1 or not isinstance(song["URLs"], list):
            print("\033[33mNo valid `URLs` provided in JSON, assuming local file.\033[0m")
            success.append(verify_local_song(s_title, s_author, LOCAL_DIR, True))
        else:
            if verify_local_song(s_title, s_author, RAW_DOWNLOAD_DIR, False) >= 0:
                print("\033[33mThe song has already been downloaded, no download is required.\033[0m")
                success.append(1)
            else:
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
                            print(f"\033[32mDownloaded the song from `{url}`.\033[0m")
                            success.append(modify_copy_raw_download(song, s_title, s_author))
                            downloaded = True
                            break
                if not downloaded:
                    print(f"\033[31mSong failed to download from the provided URLs.\033[0m")
                    success.append(-1)
                    continue
        
        # Copy to discs
        if ArgumentParser.recompile_disks:
            copy_to_discs(s_title, s_author, s_discs)
    
    print("\nDownload Results:")
    num_failed = 0
    for i in range(len(SongData.loaded_songs)):
        colour_code = ""
        if success[i] == -1:
            colour_code = "\033[31m"
            num_failed += 1
        elif success[i] == 0:
            colour_code = "\033[32m"
        elif success[i] == 1:
            colour_code = "\033[33m"
        elif success[i] == 2:
            colour_code = "\033[34m"
        print(f"{colour_code}({i + 1}/{len(SongData.loaded_songs)})-   " + str(SongData.loaded_songs[i].get("Title", "_")) + "   -   " + str(SongData.loaded_songs[i].get("Author", "_")) + "\033[0m")
    
    print(f"\n{len(SongData.loaded_songs) - num_failed}/{len(SongData.loaded_songs)} songs loaded successfully.")


class ArgumentParser:
    USAGE = """
    TODO: Write
    """
    
    recompile_disks: bool = True
    verbose: bool = False
    
    def parse_args() -> int:
        arguments = sys.argv[1:]
        while arguments:
            arg = arguments.popleft()
            if arg == "--help":
                print(ArgumentParser.USAGE)
                return 0
            if arg == "--recompile-disks":
                ArgumentParser.recompile_disks = True
                continue
            if arg == "--no-recompile-disks":
                ArgumentParser.recompile_disks = False
                continue
            if arg in ("-v", "--verbose"):
                ArgumentParser.verbose = False
                continue


def main():
    if ArgumentParser.parse_args() == 0: return
    print("Downloading...\n")
    download_audio()
    print("\nDONE")



if __name__ == '__main__':
    main()
    
    input("\nPress <ENTER> to close.\n")