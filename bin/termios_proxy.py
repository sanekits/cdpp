# termios_proxy.py
import sys
use_termios=True
use_ansiterm=True

try: # Nix only:
    import termios
    import tty
except:
    use_termios=False
    use_ansiterm=False

try: # Windows only
    import msvcrt
except:
    pass


def getraw_kbd_nix() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            ch = sys.stdin.read(1)
            yield ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def getraw_kbd_windows() -> str:
    try:
        while True:
            ch = msvcrt.getch().decode("utf-8")
            yield ch

    finally:
        pass

def getraw_kbd() -> str:
    if use_termios:
        return getraw_kbd_nix()
    return getraw_kbd_windows()
