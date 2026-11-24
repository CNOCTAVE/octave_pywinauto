## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {} pywinauto_click (@var{title}, @var{x}, @var{y})
## Activate the window whose title contains @var{title} and click at @var{x},
## @var{y}.  Pass a numeric handle instead of a string to select by HWND.
## @end deftypefn
function pywinauto_click (title, x = [], y = [])
  cfg = struct ('action', 'click');
  if (isnumeric (title))
    cfg.handle = title;
  else
    cfg.title = title;
  endif
  if (! isempty (x) && ! isempty (y))
    cfg.x = x;
    cfg.y = y;
  endif
  r = pywinauto_run (cfg);
  if (! r.ok)
    error ('pywinauto_click: %s', r.error);
  endif
endfunction
