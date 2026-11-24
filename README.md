# octave_pywinauto

Windows-only pywinauto wrapper for GNU Octave.

```octave
pkg load octave_pywinauto
pywinauto_selftest ()
w = pywinauto_windows ();
```

The pure-Python parts of pywinauto 0.6.9 / comtypes 1.5.0 are vendored as
sourceless `.pyc` for CPython 3.12 (Octave built-in) and 3.13 (ordinary
Windows Python).  `py312/` can import pywinauto on Octave's built-in
interpreter; GUI calls then use `win32_ctypes_fallback.py` because that
interpreter has no pywin32.  With a normal CPython, the real pywinauto uia
backend is used.

## Documentation

Check out document: [octave_pywinauto Document](https://cnoctave.github.io/octave_pywinauto/index.html)

## How to translate octave_pywinauto Document into another language
In ./docs directory, index.html is zh-CN simplified Chinese document.
For example, if you want to translate document into English.
1. Copy index.html as another document with different language code as filename,
   for example, en-US.html.
2. Translate en-US.html into English.
3. Add dropdown like the picture below to every *.html.
   For example, add dropdown "en-US English".
   ![the dropdown looking](./docs/translate_dropdown.png)
   The code for adding dropdown is like the picture below.
   ![the dropdown code](./docs/translate_dropdown_code.png)
4. PR to octave_pywinauto.