import os
import subprocess
import sys

try:
    import yt_dlp
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'yt-dlp'])
    # import yt_dlp

URLS = [
    "https://www.youtube.com/@artism6843/videos"
]
OUTPUT_DIR = './'
AUDIO_EXTENSION = 'm4a'

curr_dir = os.path.dirname(os.path.realpath(__file__))
relative_output_dir = os.path.join(curr_dir, OUTPUT_DIR)


def download_audio(url, output_dir=None):
    # is_playlist = False
    # is_music = False
    # with yt_dlp.YoutubeDL({}) as ydl:
    #     info = ydl.extract_info(url, download=False)
    #     if info.
    
    ydl_opts = {
        'format': f'{AUDIO_EXTENSION}/bestaudio/best',
        'outtmpl': output_dir + '/%(playlist|)s/%(title)s.%(ext)s',
        'restrictfilenames': True,
        'postprocessors': [{ # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': AUDIO_EXTENSION,
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)



def main():
    print("Downloading...\n")
    download_audio(URLS, relative_output_dir)
    print("\nDONE")



if __name__ == '__main__':
    main()