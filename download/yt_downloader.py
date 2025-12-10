import os
import subprocess
import sys

import ctypes

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

try:
    import yt_dlp
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'yt-dlp'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'yt-dlp'])
    # import yt_dlp

URLS = [
]
OUTPUT_DIR = './'
AUDIO_EXTENSION = 'mp3'

curr_dir = os.path.dirname(os.path.realpath(__file__))
relative_output_dir = os.path.join(curr_dir, OUTPUT_DIR)


def download_audio(song_refs, output_dir):
    # is_playlist = False
    # is_music = False
    # with yt_dlp.YoutubeDL({}) as ydl:
    #     info = ydl.extract_info(url, download=False)
    #     if info.
    
    success: list[int] = []
    print(output_dir)
    
    for song_ref in song_refs:
        print("\n", song_ref)
    
        if isinstance(song_ref, list) and len(song_ref) == 3:
            song, author, url = song_ref
            
            already_exists: bool = False
            if os.path.exists(f'{output_dir}\\{author}'):
                for found in os.listdir(f'{output_dir}\\{author}'):
                    if '.'.join(found.split('.')[0:-1]) == song:
                        success.append(1)
                        already_exists = True
                if already_exists:
                    continue
                
            ydl_opts = {
                'format': f'{AUDIO_EXTENSION}/bestaudio/best',
                'outtmpl': f'{output_dir}\\{author}\\{song}' + '.%(ext)s',
                'restrictfilenames': True,
                'postprocessors': [{ # Extract audio using ffmpeg
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': AUDIO_EXTENSION,
                }],
            }
        elif not isinstance(song_ref, list):
            url = song_ref
            ydl_opts = {
                'format': f'{AUDIO_EXTENSION}/bestaudio/best',
                'outtmpl': output_dir + '\\%(playlist|)s\\%(title)s.%(ext)s',
                'restrictfilenames': True,
                'postprocessors': [{ # Extract audio using ffmpeg
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': AUDIO_EXTENSION,
                }],
            }
        else:
            print("Song reference " + song_ref.__str__() + " is malformed.")
            continue

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                error_code = ydl.download(url)
            except:
                print(f"Failed to download {song_ref}")
                success.append(-1)
            else:
                success.append(0)
    
    print("\nDownload Results:")
    for i in range(len(song_refs)):
        colour_code = ""
        if success[i] == -1:
            colour_code = "\033[31m"
        elif success[i] == 0:
            colour_code = "\033[32m"
        elif success[i] == 1:
            colour_code = "\033[33m"
        print(" " + colour_code + str(song_refs[i]) + "\033[0m")



def main():
    print("Downloading...\n")
    download_audio(URLS, curr_dir)
    print("\nDONE")



if __name__ == '__main__':
    main()