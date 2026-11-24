"""Robust: locate 打开 button by class+position, click its center."""
import subprocess, time, sys, os, ctypes, ctypes.wintypes as wt
sys.path.insert(0, os.path.dirname(__file__))
from gui_shot import screenshot, list_windows
from gui_actions import foreground

user32=ctypes.WinDLL('user32',use_last_error=True)
EXE=r'E:\桌面\八度信商\octave_cn\LyricTools.exe'
SHOT_DIR=r'E:\桌面\八度信商\开源项目\octave_pywinauto\docs\screenshots'

def wait_window(sub,timeout=12):
    e=time.time()+timeout
    while time.time()<e:
        for h,t in list_windows():
            if sub in t:return h,t
        time.sleep(0.2)
    return None,None
def click(x,y):
    user32.SetCursorPos(x,y);time.sleep(0.1)
    user32.mouse_event(2,0,0,0,0);time.sleep(0.05);user32.mouse_event(4,0,0,0,0);time.sleep(0.5)
def rect(h):
    r=wt.RECT();user32.GetWindowRect(wt.HWND(h),ctypes.byref(r));return r
def cap(hwnd,name,full=False,box=None):
    foreground(hwnd);time.sleep(0.3)
    p=os.path.join(SHOT_DIR,name)
    if full and box:screenshot(p,0,x=box[0],y=box[1],w=box[2],h=box[3])
    else:screenshot(p,hwnd)
    print('CAP',name,os.path.getsize(p))

def find_controls(dlg):
    edits=[];buttons=[]
    CB=ctypes.WINFUNCTYPE(wt.BOOL,wt.HWND,wt.LPARAM)
    def cb(h,l):
        c=ctypes.create_unicode_buffer(256);user32.GetClassNameW(h,c,256)
        rr=wt.RECT();user32.GetWindowRect(h,ctypes.byref(rr))
        if c.value=='Edit':edits.append((h,rr.top))
        elif c.value=='Button':buttons.append((h,rr.left,rr.top,rr.right-rr.left,rr.bottom-rr.top))
        return True
    user32.EnumChildWindows(wt.HWND(dlg),CB(cb),0)
    return edits,buttons

def main():
    p=subprocess.Popen([EXE],cwd=os.path.dirname(EXE))
    mh,_=wait_window('动感歌词');time.sleep(0.5)
    cap(mh,'05_gui_main.png')
    r=rect(mh);click(r.left+161,r.top+178)
    vh,_=wait_window('歌词查看');time.sleep(0.5)
    cap(vh,'06_gui_viewer_empty.png')
    rv=rect(vh);foreground(vh);time.sleep(0.2)
    click(rv.left+35,rv.top+42);time.sleep(0.4)
    box=(rv.left-120,rv.top-120,1050,680)
    cap(vh,'07_gui_filemenu.png',full=True,box=box)
    click(rv.left+85,rv.top+58);time.sleep(0.8)

    dlg,_=wait_window('打开');foreground(dlg);time.sleep(0.3)
    cap(dlg,'08_gui_filedialog.png')
    edits,buttons=find_controls(dlg)
    fn=max(edits,key=lambda e:e[1])[0]
    user32.SendMessageW(wt.HWND(fn),0x000C,0,ctypes.c_wchar_p('test.qrc'))
    time.sleep(0.3)
    cap(dlg,'08b_gui_filled.png')
    # 打开 button = Button with largest left (rightmost), excluding 取消/帮助
    # print all for debug; choose rightmost button that is not 取消
    # buttons tuple = (handle, left, top, w, h). 打开/取消 sit on the same row (same top);
    # 打开 is the left one of that pair. 帮助 sits on a different row below.
    print('buttons',[(hex(b[0]),b[1],b[2],b[3],b[4]) for b in buttons])
    from collections import Counter
    row_top = Counter(b[2] for b in buttons).most_common(1)[0][0]  # most shared top = 打开/取消 row
    row = [b for b in buttons if b[2] == row_top]
    row.sort(key=lambda b: b[1])
    target = row[0]  # leftmost in row = 打开
    cx=target[1]+target[3]//2; cy=target[2]+target[4]//2
    print('click button',hex(target[0]),'at',cx,cy)
    click(cx,cy)
    time.sleep(2)
    print('--- after ---')
    for h,t in list_windows():print(hex(h),repr(t))
    vh2,_=wait_window('歌词查看')
    if vh2:cap(vh2,'09_gui_plaintext.png')
    time.sleep(0.5);p.terminate()
if __name__=='__main__':main()
