# pip install python-vlc

IGNORED_FOLDERS = ['download']
ALLOWED_AUDIO_FORMATS = ['wav', 'm4a', 'mp4']
PROGRESS_STEPS = 50

###########################################

# Try to install vlc
try:
    import vlc
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-vlc"])
    import vlc

# Try to install pyinput
try:
    from pynput.keyboard import Key, Listener
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput.keyboard import Key, Listener

###########################################

import sys
clear_command = lambda: ()
match sys.platform:
    case 'aix':
        pass
    case 'android':
        pass
    case 'emscripten':
        pass
    case 'ios':
        pass
    case 'linux':
        clear_command = lambda: os.system('clear')
    case 'darwin':
        clear_command = lambda: os.system('clear')
    case 'win32':
        clear_command = lambda: os.system('cls')
    case 'cygwin':
        pass
    case 'wasi':
        pass

###########################################

import asyncio

def on_press(key):
    print('{0} pressed'.format(
        key))

def on_release(key):
    print('{0} release'.format(
        key))
    if key == Key.esc:
        # Stop listener
        return False

# Collect events until released
async def prepare_keyboard_listener():
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

# asyncio.run(prepare_keyboard_listener())

###########################################

import pathlib, os, random, time, sys

main_folder = pathlib.Path(__file__).parent.absolute()

async def is_valid_playlist_folder(folder: str):
    """Return whether or not the given folder/file is a
    valid playlist/song.
    """
    if (folder[0] == '.'): return False
    if (folder in IGNORED_FOLDERS): return False
    
    correct_format = False
    for format in ALLOWED_AUDIO_FORMATS:
        if folder.endswith('.' + format):
            correct_format = True
    if (not correct_format) and ('.' in folder): return False
    
    return True

last_folders = []
async def select_song() -> pathlib.Path:
    """Return the path of a randomly selected song.
    
    Playlists/songs that have just been played are avoided.
    """
    global last_folders
    new_folders = []
    depth = 0
    while depth < 100:
        curr_path = pathlib.Path(main_folder, *new_folders)
        if not curr_path.is_dir():
            break
        
        sub_folders = [folder.name for folder in os.scandir(curr_path) if is_valid_playlist_folder(folder.name)]
        
        if len(sub_folders) <= 0:
            break
        
        if len(last_folders) > depth:
            picky_sub_folders = [folder for folder in sub_folders if folder != last_folders[depth]]
            if len(picky_sub_folders) > 0:
                sub_folders = picky_sub_folders
        
        new_folders.append(random.choice(sub_folders))
        depth += 1
    
    last_folders = new_folders
    return pathlib.Path(os.path.join(main_folder, *new_folders))

async def write_display(duration: float, progress: int):
    """Return `None`. Rewrite the TUI to the console/shell/terminal.
    """
    clear_command()
    
    print(f"Listening to: {last_folders[-1]}")
    
    if len(last_folders[0:-1]) > 0: print(f"From:         {'/'.join(last_folders[0:-1])}")
    
    print()
    
    print('#'*progress + '_'*(PROGRESS_STEPS-progress) + f' ({int(progress / PROGRESS_STEPS * 100)} %)')
    seconds, minutes, hours, days = (
        duration / 1000 % 60,
        int(duration / 1000 / 60 % 60),
        int(duration / 1000 / 60 / 60 % 24),
        int(duration / 1000 / 60 / 60 / 24)
    )
    
    print(
        "Duration:" +
        (f" {days} days," if days > 0 else '') +
        (f" {hours}h," if hours > 0 else '') +
        (f" {minutes}min," if minutes > 0 else '') +
        " {:.4f}s".format(seconds)
    )

async def play_new_song():
    """Return `None`. Play a new, randomly-selected
    song using VLC. Refresh the TUI once every
    `duration/PROGRESS_STEPS` miliseconds.
    """
    instance = vlc.Instance()
    player = instance.media_player_new()
    
    selected_song = await select_song()
    media = instance.media_new(selected_song)
    player.set_media(media)
    player.play()
    time.sleep(0.5)
    duration = player.get_length()
    await write_display(duration, 0)
    
    for i in range(1, PROGRESS_STEPS+1):
        time.sleep(duration / PROGRESS_STEPS / 1000)
        await write_display(duration, i)

###########################################

async def main():
    while True:
        await play_new_song()

if __name__ == '__main__':
    asyncio.gather(main(), prepare_keyboard_listener())
