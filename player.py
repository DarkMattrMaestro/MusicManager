# pip install python-vlc

IGNORED_FOLDERS = ['download', 'discs']
ALLOWED_AUDIO_FORMATS = ['wav', 'm4a', 'mp3', 'aac', 'flac', 'ogg']
CONDITION_CHECK_TIMESTEP = 2 # in seconds
PROGRESS_STEPS = 50
VOLUME_INCREMENT = 5 # in percent

WINDOW_NAME = "Maestro's Music Player"

COMMANDS_INFO = """Commands:
(<esc>) Quit;

Global Hotkeys:
(<ctrl> + <alt> + 's') Skip;
(<ctrl> + <alt> + 'p') Pause;
(<ctrl> + <alt> + '+') Decrease volume;
(<ctrl> + <alt> + '-') Decrease volume;"""

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
    from pynput.keyboard import Key, Listener, GlobalHotKeys, HotKey
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput"])
    from pynput.keyboard import Key, Listener, GlobalHotKeys, HotKey

# Try to install pywinctl
try:
    import pywinctl as pwc
except:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywinctl"])
    import pywinctl as pwc

###########################################

import math
import sys
clear_commands = []#[lambda: (sys.stdout.flush())]
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
        clear_commands.append(lambda: os.system('clear'))
    case 'darwin':
        clear_commands.append(lambda: os.system('clear'))
    case 'win32':
        clear_commands.append(lambda: os.system('cls'))
    case 'cygwin':
        pass
    case 'wasi':
        pass
clear_command = lambda: [command() for command in clear_commands]

###########################################

import threading

s_print_lock = threading.Lock()

def s_print(*a, **b):
    """Thread safe print function
    """
    with s_print_lock:
        print(*a, **b, flush=True)

###########################################

import pathlib, os, random, time, sys

main_folder = pathlib.Path(__file__).parent.absolute()

class MusicPlayer:
    skip_event: threading.Event = None
    pause_event: threading.Event = None
    instance: vlc.Instance = None
    player: vlc.MediaPlayer = None
    
    is_writing_display = False
    
    last_folders = []
    
    progress = 0
    duration = 0
    
    def __init__(self):
        self.skip_event = threading.Event()
        self.pause_event = threading.Event()
        
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
    
    @staticmethod
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

    def select_song(self) -> pathlib.Path:
        """Return the path of a randomly selected song.
        
        Playlists/songs that have just been played are avoided.
        """
        new_folders = []
        depth = 0
        while depth < 100:
            curr_path = pathlib.Path(main_folder, *new_folders)
            if not curr_path.is_dir():
                break
            
            sub_folders = [folder.name for folder in os.scandir(curr_path) if MusicPlayer.is_valid_playlist_folder(folder.name)]
            
            if len(sub_folders) <= 0:
                break
            
            if len(self.last_folders) > depth:
                picky_sub_folders = [folder for folder in sub_folders if folder != self.last_folders[depth]]
                if len(picky_sub_folders) > 0:
                    sub_folders = picky_sub_folders
            
            new_folders.append(random.choice(sub_folders))
            depth += 1
        
        self.last_folders = new_folders
        return pathlib.Path(os.path.join(main_folder, *new_folders))
    
    def write_display(self):
        """Return `None`. Rewrite the TUI to the console/shell/terminal.
        """
        clear_command()
        
        seconds, minutes, hours, days = (
            self.duration / 1000 % 60,
            int(self.duration / 1000 / 60 % 60),
            int(self.duration / 1000 / 60 / 60 % 24),
            int(self.duration / 1000 / 60 / 60 / 24)
        )
        
        s_print(
            f"Listening to: {self.last_folders[-1]}",
            
            f"From:         {'/'.join(self.last_folders[0:-1])}" if len(self.last_folders[0:-1]) > 0 else "",
            
            "",
            
            '\x1b[92m'+'#'*self.progress + '\x1b[90m'+'_'*(PROGRESS_STEPS-self.progress) + '\x1b[0m' + f' ({int(self.progress / PROGRESS_STEPS * 100)} %)',
            
            "Duration:" +
            (f" {days} days," if days > 0 else '') +
            (f" {hours}h," if hours > 0 else '') +
            (f" {minutes}min," if minutes > 0 else '') +
            " {:.4f}s".format(seconds),
            
            f'Volume: {self.player.audio_get_volume()} %',
            
            "",
            
            COMMANDS_INFO,
            sep = '\n'
        )

    def play_new_song(self):
        """Return 0 if successful, 1 if cancelled, else -1. Play a new, randomly-selected
        song using VLC. Refresh the TUI once every
        `duration/PROGRESS_STEPS` miliseconds.
        """
        attempts = 10
        while (attempts > 0):
            attempts -= 1
            selected_song = self.select_song()
            if selected_song.is_file(): break
        if attempts <= 0: return -1
        
        media = self.instance.media_new(selected_song)
        self.player.set_media(media)
        self.player.play()
        time.sleep(0.5)
        self.duration = self.player.get_length()
        self.progress = 0
        self.write_display()
        
        for attempts in range(0, 100):
            substep_iterations = math.ceil((self.duration / 1000 / PROGRESS_STEPS) / CONDITION_CHECK_TIMESTEP)
            if substep_iterations > 0: break
            time.sleep(0.5)
            self.duration = self.player.get_length()
        substep_timestep = (self.duration / 1000 / PROGRESS_STEPS) / substep_iterations
        
        # Progress-bar updates
        for self.progress in range(1, PROGRESS_STEPS+1):
            # Substep checks for events
            for j in range(0, substep_iterations):
                time.sleep(substep_timestep)
                if (self.skip_event.is_set()): return 1
                
                # Process pausing
                was_paused = self.pause_event.is_set()
                if was_paused:
                    self.player.pause()
                    clear_command()
                    s_print('Paused...')
                while self.pause_event.is_set():
                    time.sleep(0.5)
                if was_paused:
                    self.player.play()
                
            self.write_display()
        
        return 0
    
    def main_loop(self):
        while self.play_new_song() >= 0:
            self.skip_event.clear()

###########################################

class KeyboardManager:
    music_player: MusicPlayer
    
    def __init__(self, music_player: MusicPlayer):
        self.music_player = music_player
    
    def on_skip(self):
        clear_command()
        s_print('skipping...')
        self.music_player.skip_event.set()
        self.music_player.player.stop()
    
    def on_pause(self):
        if not self.music_player.pause_event.is_set():
            self.music_player.pause_event.set()
            clear_command()
            s_print('Pausing...')
        else:
            self.music_player.pause_event.clear()
            

    def on_volume_up(self):
        self.music_player.player.audio_set_volume(min(100, self.music_player.player.audio_get_volume() + VOLUME_INCREMENT))
        
        self.music_player.write_display()

    def on_volume_down(self):
        self.music_player.player.audio_set_volume(max(0, self.music_player.player.audio_get_volume() - VOLUME_INCREMENT))
        
        self.music_player.write_display()

    # Collect events until released
    def prepare_keyboard_listener(self):
        def active(f):
            if (pwc.getActiveWindowTitle() == WINDOW_NAME): f()
        
        with GlobalHotKeys({
            '<esc>': lambda: active(sys.exit),
            '<ctrl>+<alt>+s': self.on_skip,
            '<ctrl>+<alt>+p': self.on_pause,
            '<ctrl>+<alt>+=': self.on_volume_up,
            '<ctrl>+<alt>+-': self.on_volume_down
        }) as h:
            h.join()

###########################################

output_thread = None
if __name__ == '__main__':
    os.system("title " + WINDOW_NAME)
    
    music_player: MusicPlayer = MusicPlayer()
    keyboard_manager: KeyboardManager = KeyboardManager(music_player)
    
    output_thread = threading.Thread(target=music_player.main_loop, daemon=True)
    output_thread.start()
    
    keyboard_manager.prepare_keyboard_listener()
