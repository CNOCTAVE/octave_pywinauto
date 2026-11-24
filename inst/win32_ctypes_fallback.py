# Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
# SPDX-License-Identifier: GPL-3.0-or-later
"""Minimal ctypes Win32 backend for octave_pywinauto.

Octave's Windows build ships CPython 3.12 without pywin32, so the vendored
pywinauto .pyc files can be imported but their ``win32gui`` backend cannot be
loaded.  This module supplies the small subset of window operations that the
Octave wrapper needs, using only ctypes and the Win32 API.  When pywin32 *is*
available, pywinauto_driver.py uses the real pywinauto backend instead.
"""
import ctypes
from ctypes import wintypes
import subprocess
import time

_dll = getattr(ctypes, "WinDLL", ctypes.CDLL)

def _load(name):
    try:
        return _dll(name, use_last_error=True)
    except OSError:
        return _dll("/c/Windows/System32/" + name + ".dll", use_last_error=True)

_winfunctype = getattr (ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

u32 = _load("user32")
k32 = _load("kernel32")

WM_CLOSE = 0x0010
WM_SETTEXT = 0x000C
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
SW_RESTORE = 9

u32.EnumWindows.argtypes = [_winfunctype(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM), wintypes.LPARAM]
u32.EnumWindows.restype = wintypes.BOOL
u32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
u32.GetWindowTextLengthW.restype = ctypes.c_int
u32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
u32.GetWindowTextW.restype = ctypes.c_int
u32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
u32.GetClassNameW.restype = ctypes.c_int
u32.IsWindowVisible.argtypes = [wintypes.HWND]
u32.IsWindowVisible.restype = wintypes.BOOL
u32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
u32.GetWindowThreadProcessId.restype = wintypes.DWORD
u32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
u32.GetWindowRect.restype = wintypes.BOOL
u32.SetForegroundWindow.argtypes = [wintypes.HWND]
u32.SetForegroundWindow.restype = wintypes.BOOL
u32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
u32.ShowWindow.restype = wintypes.BOOL
u32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
u32.SetCursorPos.restype = wintypes.BOOL
u32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p]
u32.mouse_event.restype = None
u32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPCWSTR]
u32.SendMessageW.restype = ctypes.c_ssize_t

INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_KEYUP = 0x0002


class _KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("ki", _KEYBDINPUT), ("padding", ctypes.c_byte * 32)]


class _INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


u32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(_INPUT), ctypes.c_int]
u32.SendInput.restype = wintypes.UINT


def _text(hwnd, len_fn, get_fn):
    n = len_fn(hwnd)
    buf = ctypes.create_unicode_buffer(max(n + 1, 2))
    get_fn(hwnd, buf, len(buf))
    return buf.value


def windows(visible_only=True):
    out = []

    @_winfunctype(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        if visible_only and not u32.IsWindowVisible(hwnd):
            return True
        title = _text(hwnd, u32.GetWindowTextLengthW, u32.GetWindowTextW)
        if not title:
            return True
        cls = ctypes.create_unicode_buffer(256)
        u32.GetClassNameW(hwnd, cls, 256)
        pid = wintypes.DWORD()
        u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        rect = RECT()
        u32.GetWindowRect(hwnd, ctypes.byref(rect))
        out.append({"handle": int(hwnd), "title": title, "class": cls.value,
                    "pid": int(pid.value),
                    "rect": [rect.left, rect.top, rect.right, rect.bottom]})
        return True

    u32.EnumWindows(cb, 0)
    return out


def find_window(title=None, handle=None, contains=True):
    for w in windows():
        if handle is not None and w["handle"] == int(handle):
            return w
        if title is not None:
            if contains and title in w["title"]:
                return w
            if not contains and title == w["title"]:
                return w
    return None


def activate(hwnd):
    hwnd = int(hwnd)
    u32.ShowWindow(hwnd, SW_RESTORE)
    u32.SetForegroundWindow(hwnd)
    time.sleep(0.15)


def click(hwnd, x=None, y=None):
    hwnd = int(hwnd)
    activate(hwnd)
    if x is None or y is None:
        rect = RECT()
        u32.GetWindowRect(hwnd, ctypes.byref(rect))
        x = (rect.left + rect.right) // 2
        y = (rect.top + rect.bottom) // 2
    u32.SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    u32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, None)
    time.sleep(0.05)
    u32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, None)


def type_keys(text, hwnd=None):
    if hwnd is not None:
        u32.SendMessageW(int(hwnd), WM_SETTEXT, 0, text)
        return True
    for ch in text:
        if ch in "\r\n":
            continue
        for flags in (KEYEVENTF_UNICODE, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP):
            inp = _INPUT()
            inp.type = INPUT_KEYBOARD
            inp.ki = _KEYBDINPUT(0, ord(ch), flags, 0, None)
            if u32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp)) != 1:
                return False
        time.sleep(0.01)
    return True


def close_window(hwnd):
    return bool(u32.SendMessageW(int(hwnd), WM_CLOSE, 0, None))


def start(exe, args=None):
    argv = [exe] + list(args or [])
    proc = subprocess.Popen(argv)
    return proc.pid


def pid_alive(pid):
    h = k32.OpenProcess(0x1000, False, int(pid))
    if not h:
        return False
    k32.CloseHandle(h)
    return True
