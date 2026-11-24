## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
## Print the active pywinauto backend and its Python version.
function pywinauto_version ()
  ctx = pywinauto_init ();
  r = pywinauto_run (struct ('action', 'version'));
  printf ('pywinauto backend=%s python=%s\n', r.backend, r.python);
endfunction
