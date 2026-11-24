"""Pure-ctypes Windows screenshot + window utility. No third-party deps."""
import ctypes, ctypes.wintypes as wt, struct, zlib, sys, os

user32 = ctypes.WinDLL('user32', use_last_error=True)
gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)

# ---- GDI screenshot ----
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [('biSize', wt.DWORD), ('biWidth', wt.LONG), ('biHeight', wt.LONG),
                ('biPlanes', wt.WORD), ('biBitCount', wt.WORD), ('biCompression', wt.DWORD),
                ('biSizeImage', wt.DWORD), ('biXPelsPerMeter', wt.LONG), ('biYPelsPerMeter', wt.LONG),
                ('biClrUsed', wt.DWORD), ('biClrImportant', wt.DWORD)]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [('bmiHeader', BITMAPINFOHEADER), ('bmiColors', wt.DWORD * 3)]

def screenshot(path, hwnd=0, x=None, y=None, w=None, h=None):
    """Capture full screen (hwnd=0) or a window rect. Save as PNG."""
    if hwnd:
        r = wt.RECT()
        user32.GetWindowRect(wt.HWND(hwnd), ctypes.byref(r))
        x, y, w, h = r.left, r.top, r.right - r.left, r.bottom - r.top
    else:
        x = 0 if x is None else x
        y = 0 if y is None else y
        w = user32.GetSystemMetrics(0) if w is None else w
        h = user32.GetSystemMetrics(1) if h is None else h
    hdc = user32.GetDC(0)
    mdc = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    gdi32.SelectObject(mdc, bmp)
    gdi32.BitBlt(mdc, 0, 0, w, h, hdc, x, y, 0x00CC0020)  # SRCCOPY
    bi = BITMAPINFO()
    bi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bi.bmiHeader.biWidth = w
    bi.bmiHeader.biHeight = -h  # top-down
    bi.bmiHeader.biPlanes = 1
    bi.bmiHeader.biBitCount = 32
    bi.bmiHeader.biCompression = 0
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bi), 0)
    raw = buf.raw
    # BGRA -> RGB rows
    rows = []
    stride = w * 4
    for yy in range(h):
        row = raw[yy*stride:(yy+1)*stride]
        rgb = bytearray()
        for xx in range(w):
            b, g, r = row[xx*4], row[xx*4+1], row[xx*4+2]
            rgb += bytes((r, g, b))
        rows.append(b'\x00' + bytes(rgb))
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(b''.join(rows), 6))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(mdc)
    user32.ReleaseDC(0, hdc)
    return path, w, h

# ---- window enum ----
WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def list_windows():
    out = []
    def cb(hwnd, lp):
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        if n == 0:
            return True
        b = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, b, n + 1)
        out.append((hwnd, b.value))
        return True
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return out

def find_window(substr):
    for hwnd, title in list_windows():
        if substr.lower() in title.lower():
            return hwnd, title
    return None, None

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        for hwnd, title in list_windows():
            print(hex(hwnd), repr(title))
    elif cmd == 'shot':
        path = sys.argv[2]
        hwnd = 0
        if len(sys.argv) > 3 and sys.argv[3] != '0':
            hwnd = int(sys.argv[3], 0)
        p, w, h = screenshot(path, hwnd)
        print('saved', p, w, 'x', h, os.path.getsize(p), 'bytes')
