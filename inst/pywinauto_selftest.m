## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {} pywinauto_selftest ()
## Verify the wrapper: print the active backend and enumerate visible windows.
## No GUI action is performed, so this test is safe to run anywhere on Windows.
## @end deftypefn
function pywinauto_selftest ()
  r = pywinauto_run (struct ('action', 'version'));
  printf ('backend=%s python=%s\n', r.backend, r.python);
  w = pywinauto_windows ();
  printf ('visible windows: %d\n', numel (w));
  for i = 1:min (5, numel (w))
    printf ('  - %s\n', w(i).title);
  endfor
endfunction
