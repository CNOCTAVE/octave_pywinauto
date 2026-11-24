## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
## Close the window whose title contains the given string (or with HWND).
function pywinauto_close (title)
  cfg = struct ('action', 'close');
  if (isnumeric (title))
    cfg.handle = title;
  else
    cfg.title = title;
  endif
  r = pywinauto_run (cfg);
  if (! r.ok)
    error ('pywinauto_close: %s', r.error);
  endif
endfunction
