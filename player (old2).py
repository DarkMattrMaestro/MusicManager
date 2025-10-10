# pip install python-vlc

IGNORED_FOLDERS = ['download']
ALLOWED_AUDIO_FORMATS = ['wav', 'm4a', 'mp3', 'aac', 'flac', 'ogg']
CONDITION_CHECK_TIMESTEP = 2 # in seconds
PROGRESS_STEPS = 50
VOLUME_INCREMENT = 5 # in percent

commands_info = """(<ctrl>+<alt>+s) skip;"""

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
    from pynput.keyboard import Key, Listener, GlobalHotKeys
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput.keyboard import Key, Listener, GlobalHotKeys

###########################################

import math
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

import threading

s_print_lock = threading.Lock()

def s_print(*a, **b):
    """Thread safe print function
    """
    with s_print_lock:
        print(*a, **b)

###########################################

def on_skip():
    clear_command()
    print('skipping...')
    skip_event.set()
    player.stop()

def on_volume_up():
    player.audio_set_volume(min(100, player.audio_get_volume() + VOLUME_INCREMENT))

def on_volume_down():
    player.audio_set_volume(max(0, player.audio_get_volume() - VOLUME_INCREMENT))

# Collect events until released
def prepare_keyboard_listener():
    with GlobalHotKeys({
        '<ctrl>+<alt>+s': on_skip,
        '<ctrl>+v+=': on_volume_up,
        '<ctrl>+v+-': on_volume_down
    }) as h:
        h.join()

###########################################

import pathlib, os, random, time, sys

main_folder = pathlib.Path(__file__).parent.absolute()

def is_valid_playlist_folder(folder: str):
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
def select_song() -> pathlib.Path:
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

def write_display(duration: float, progress: int):
    """Return `None`. Rewrite the TUI to the console/shell/terminal.
    """
    clear_command()
    
    s_print(f"Listening to: {last_folders[-1]}")
    
    if len(last_folders[0:-1]) > 0: s_print(f"From:         {'/'.join(last_folders[0:-1])}")
    
    s_print()
    
    s_print('\x1b[92m'+'#'*progress + '\x1b[90m'+'_'*(PROGRESS_STEPS-progress) + '\x1b[0m' + f' ({int(progress / PROGRESS_STEPS * 100)} %)')
    seconds, minutes, hours, days = (
        duration / 1000 % 60,
        int(duration / 1000 / 60 % 60),
        int(duration / 1000 / 60 / 60 % 24),
        int(duration / 1000 / 60 / 60 / 24)
    )
    
    s_print(
        "Duration:" +
        (f" {days} days," if days > 0 else '') +
        (f" {hours}h," if hours > 0 else '') +
        (f" {minutes}min," if minutes > 0 else '') +
        " {:.4f}s".format(seconds)
    )
    
    s_print(f'Volume: {player.audio_get_volume()} %')
    
    s_print()
    
    s_print("Commands:\n" + commands_info)

def play_new_song(skip_event: threading.Event):
    """Return 0 if successful, 1 if cancelled, else -1. Play a new, randomly-selected
    song using VLC. Refresh the TUI once every
    `duration/PROGRESS_STEPS` miliseconds.
    """
        
    attempts = 10
    while (attempts > 0):
        attempts -= 1
        selected_song = select_song()
        if selected_song.is_file(): break
    if attempts <= 0: return -1
    
    media = instance.media_new(selected_song)
    player.set_media(media)
    player.play()
    time.sleep(0.5)
    duration = player.get_length()
    write_display(duration, 0)
    
    substep_iterations = math.ceil((duration / 1000 / PROGRESS_STEPS) / CONDITION_CHECK_TIMESTEP)
    substep_timestep = (duration / 1000 / PROGRESS_STEPS) / substep_iterations
    
    # Progress-bar updates
    for i in range(1, PROGRESS_STEPS+1):
        # Substep checks for events
        for j in range(0, substep_iterations):
            if (skip_event.is_set()): return 1
            time.sleep(substep_timestep)
        
        write_display(duration, i)
    
    return 0

###########################################

def main(skip_event: threading.Event):
    while play_new_song(skip_event) >= 0:
        skip_event.clear()

skip_event = threading.Event()
output_thread = None
if __name__ == '__main__':
    instance: vlc.Instance = vlc.Instance()
    player: vlc.MediaPlayer = instance.media_player_new()
    
    output_thread = threading.Thread(target=main, args=(skip_event,), daemon=True)
    output_thread.start()
    prepare_keyboard_listener()
    # prepare_keyboard_listener()
    # main()
