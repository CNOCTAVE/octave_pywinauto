# Vendored pywinauto bytecode

`py312/` and `py313/` contain sourceless `.pyc` files compiled from
pywinauto 0.6.9, comtypes 1.5.0 and six 1.17.0.  Rebuild with:

```sh
python tools/compile_pyc.py <site-packages-dir> inst/vendor/pyXYZ
```

Octave's Windows build embeds CPython 3.12 without pip and without pywin32.
`py312/` lets that interpreter `import pywinauto`; the GUI operations
themselves are served by `inst/win32_ctypes_fallback.py`, a small ctypes
wrapper around user32/kernel32.  With a normal CPython that has pywin32,
the real pywinauto backend is selected automatically.

`pywinauto_init()` probes `PYWINAUTO_PYTHON`, `python3`, `python`, `py -3`
and `$OCTAVE_HOME/usr/bin/python.exe`, then reports the active backend through
`pywinauto_version()`.
