"""GUI actions via ctypes: foreground, click, keys, capture."""
import ctypes, ctypes.wintypes as wt, sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from gui_shot import screenshot, find_window, list_windows

user32 = ctypes.WinDLL('user32', use_last_error=True)

def foreground(hwnd):
    user32.ShowWindow(wt.HWND(hwnd), 9)  # SW_RESTORE
    user32.SetForegroundWindow(wt.HWND(hwnd))
    time.sleep(0.3)

def click(hwnd, x, y):
    """Click at client-relative (x,y) inside hwnd."""
    foreground(hwnd)
    user32.SetCursorPos(x, y)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
    time.sleep(0.3)

def capture(hwnd, path):
    foreground(hwnd)
    time.sleep(0.2)
    return screenshot(path, hwnd)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'cap':
        hwnd = int(sys.argv[2], 0)
        capture(hwnd, sys.argv[3])
        print('captured')
