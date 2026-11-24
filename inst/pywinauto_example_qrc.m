## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {@var{info} =} pywinauto_example_qrc (@var{exe}, @var{qrc})
## Automate LyricTools.exe: start it with @var{qrc} as argument, wait for the
## window, and report the windows that appeared.  This is the GUI step used
## while cross-checking the QRC decryption against the original program.
## @end deftypefn
function info = pywinauto_example_qrc (exe, qrc)
  before = pywinauto_windows ();
  pid = pywinauto_start (exe, {qrc});
  pause (2);
  after = pywinauto_windows ();
  titles = {after.title};
  info = struct ('pid', pid, 'exe', exe, 'qrc', qrc, 'window_count', numel (after), 'titles', {titles});
endfunction
