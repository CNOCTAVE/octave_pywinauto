## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
## Connect to an already running process id; returns the pid on success.
function pid = pywinauto_connect (pid)
  r = pywinauto_run (struct ('action', 'connect', 'pid', pid));
  if (! r.ok)
    error ('pywinauto_connect: %s', r.error);
  endif
  pid = r.pid;
endfunction
