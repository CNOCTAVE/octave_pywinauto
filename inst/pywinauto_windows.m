## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {@var{w} =} pywinauto_windows ()
## Return a struct array describing all visible top-level windows.
## Fields: handle, title, class, pid, rect (ctypes backend only).
## @end deftypefn
function w = pywinauto_windows ()
  r = pywinauto_run (struct ('action', 'windows'));
  if (! r.ok)
    error ('pywinauto_windows: %s', r.error);
  endif
  w = r.windows;
endfunction
