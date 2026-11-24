#!/usr/bin/env python3
"""Compile the vendored pure-Python sources into sourceless .pyc files.

Usage: python tools/compile_pyc.py <pywinauto_site_packages> <output_dir>

Run once per CPython version that Octave may use.  The Octave Windows build
ships CPython 3.12, while an ordinary Windows Python is usually 3.13; the
bytecode magic differs, so both flavours are vendored separately.
"""
import os
import py_compile
import re
import sys
import tempfile

SOURCES = ("pywinauto", "comtypes")
MODULES = ("six.py",)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: compile_pyc.py <site-packages> <output-dir>")
    root, out = sys.argv[1], sys.argv[2]
    count = 0
    for name in SOURCES:
        src_root = os.path.join(root, name)
        if not os.path.isdir(src_root):
            print("skip missing", src_root)
            continue
        for dirpath, dirnames, filenames in os.walk(src_root):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            rel = os.path.relpath(dirpath, root)
            dst_dir = os.path.join(out, rel)
            os.makedirs(dst_dir, exist_ok=True)
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                src = os.path.join(dirpath, fn)
                dst = os.path.join(dst_dir, fn + "c")
                try:
                    with open(src, "rb") as fh:
                        raw = fh.read()
                    if b"coding: mbcs" in raw or b"coding=mbcs" in raw:
                        # MSYS2 CPython has no `mbcs` codec; these generated
                        # comtypes files are pure ASCII in practice.
                        raw = re.sub(rb"coding[:=]\s*mbcs", b"coding=utf-8", raw)
                        fd, tmp = tempfile.mkstemp(suffix=".py")
                        try:
                            with os.fdopen(fd, "wb") as tf:
                                tf.write(raw)
                            py_compile.compile(tmp, cfile=dst, doraise=True)
                        finally:
                            os.unlink(tmp)
                    else:
                        py_compile.compile(src, cfile=dst, doraise=True)
                    count += 1
                except py_compile.PyCompileError as exc:
                    print("WARN", src, exc)
    for mod in MODULES:
        src = os.path.join(root, mod)
        if os.path.isfile(src):
            py_compile.compile(src, cfile=os.path.join(out, mod + "c"), doraise=True)
            count += 1
    print(f"compiled {count} .pyc into {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
