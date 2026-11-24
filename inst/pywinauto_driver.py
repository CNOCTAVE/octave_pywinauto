#!/usr/bin/env python3
# Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
# SPDX-License-Identifier: GPL-3.0-or-later
"""
pywinauto_driver.py -- GUI automation backend for octave_pywinauto.

Reads a JSON config, performs one action and writes a JSON result.  Two
backends are available:

  * pywinauto -- used when the interpreter can import pywinauto *and* its
    win32gui dependency (normal CPython on Windows).
  * ctypes fallback -- used with Octave's built-in CPython 3.12, which has no
    pywin32.  The vendored pywinauto .pyc files are still on sys.path, and the
    fallback implements the small Win32 subset the Octave API exposes.
"""
import json
import os
import re
import sys

def fix_path(p):
    """Accept both Windows and MSYS2-style paths (Octave's built-in Python)."""
    p = str(p).replace("\\", "/")
    if os.name == "nt":
        return p
    return re.sub(r"^([A-Za-z]):/", lambda m: "/" + m.group(1).lower() + "/", p)

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor", "py%d%d" % sys.version_info[:2])
if VENDOR not in sys.path:
    sys.path.insert(0, VENDOR)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    import pywinauto  # noqa: F401
    from pywinauto import Desktop, Application
    import win32gui  # noqa: F401
    BACKEND = "pywinauto"
except Exception:
    Desktop = None
    Application = None
    import win32_ctypes_fallback as fb
    BACKEND = "ctypes"


def real_windows():
    out = []
    for w in Desktop(backend="uia").windows():
        try:
            out.append({"handle": w.handle, "title": w.window_text(),
                        "class": w.class_name(), "pid": w.process_id()})
        except Exception:
            continue
    return out


def real_find(cfg):
    desk = Desktop(backend="uia")
    if cfg.get("handle"):
        return desk.window(handle=int(cfg["handle"])).wrapper_object()
    kwargs = {}
    if cfg.get("title"):
        kwargs["title_re"] = ".*" + cfg["title"] + ".*"
    if cfg.get("class_name"):
        kwargs["class_name"] = cfg["class_name"]
    return desk.window(**kwargs).wrapper_object()


def perform(cfg):
    action = cfg.get("action", "version")
    if action == "version":
        return {"backend": BACKEND, "python": sys.version.split()[0]}

    if action == "windows":
        if BACKEND == "pywinauto":
            return {"windows": real_windows()}
        return {"windows": fb.windows()}

    if action == "start":
        if BACKEND == "pywinauto":
            app = Application(backend="uia")
            app.start(cfg["exe"])
            return {"pid": app.process}
        return {"pid": fb.start(cfg["exe"], cfg.get("args", []))}

    if action == "connect":
        if BACKEND == "pywinauto":
            app = Application(backend="uia").connect(process=int(cfg["pid"]))
            return {"pid": app.process}
        pid = int(cfg["pid"])
        if not fb.pid_alive(pid):
            raise RuntimeError("process %d is not running" % pid)
        return {"pid": pid}

    if action == "click":
        if BACKEND == "pywinauto":
            real_find(cfg).click_input(coords=(cfg.get("x", 5), cfg.get("y", 5)))
        else:
            w = fb.find_window(cfg.get("title"), cfg.get("handle"))
            if w is None:
                raise RuntimeError("window not found: %s" % cfg.get("title"))
            fb.click(w["handle"], cfg.get("x"), cfg.get("y"))
        return {"clicked": True}

    if action == "type_keys":
        if BACKEND == "pywinauto":
            from pywinauto.keyboard import send_keys
            send_keys(cfg["text"])
        else:
            hwnd = None
            if cfg.get("title") or cfg.get("handle"):
                w = fb.find_window(cfg.get("title"), cfg.get("handle"))
                if w is None:
                    raise RuntimeError("window not found: %s" % cfg.get("title"))
                hwnd = w["handle"]
                fb.activate(hwnd)
            fb.type_keys(cfg["text"], hwnd if cfg.get("set_text") else None)
        return {"typed": cfg["text"]}

    if action == "close":
        if BACKEND == "pywinauto":
            real_find(cfg).close()
        else:
            w = fb.find_window(cfg.get("title"), cfg.get("handle"))
            if w is None:
                raise RuntimeError("window not found: %s" % cfg.get("title"))
            fb.close_window(w["handle"])
        return {"closed": True}

    if action == "texts":
        if BACKEND == "pywinauto":
            return {"texts": [w.window_text() for w in real_find(cfg).children()]}
        w = fb.find_window(cfg.get("title"), cfg.get("handle"))
        if w is None:
            raise RuntimeError("window not found")
        return {"texts": [w["title"]]}

    raise RuntimeError("unknown action: %s" % action)


def main():
    if len(sys.argv) < 2:
        print("usage: pywinauto_driver.py <config.json>", file=sys.stderr)
        return 2
    cfg_path = fix_path(sys.argv[1])
    with open(cfg_path, "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    cfg["result_file"] = fix_path(cfg["result_file"])
    if "exe" in cfg:
        cfg["exe"] = fix_path(cfg["exe"])
    result = {"ok": False, "error": "", "backend": BACKEND}
    try:
        result.update(perform(cfg))
        result["ok"] = True
    except Exception as exc:  # noqa: BLE001 -- returned to Octave
        result["error"] = "%s: %s" % (type(exc).__name__, exc)
    with open(cfg["result_file"], "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
