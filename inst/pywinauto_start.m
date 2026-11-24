## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {@var{pid} =} pywinauto_start (@var{exe})
## @deftypefnx {} {@var{pid} =} pywinauto_start (@var{exe}, @var{args})
## Start @var{exe} and return its process id.
## @end deftypefn
function pid = pywinauto_start (exe, args = {})
  if (ischar (args))
    args = {args};
  endif
  cfg = struct ('action', 'start', 'exe', exe, 'args', args);
  r = pywinauto_run (cfg);
  if (! r.ok)
    error ('pywinauto_start: %s', r.error);
  endif
  pid = r.pid;
endfunction
