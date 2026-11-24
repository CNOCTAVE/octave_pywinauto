## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {} pywinauto_type_keys (@var{text})
## @deftypefnx {} {} pywinauto_type_keys (@var{text}, @var{title})
## @deftypefnx {} {} pywinauto_type_keys (@var{text}, @var{title}, true)
## Send @var{text} to the active window, or to the window whose title contains
## @var{title}.  With the third argument true the ctypes backend sets the
## window text directly instead of synthesising keystrokes.
## @end deftypefn
function pywinauto_type_keys (text, title = '', set_text = false)
  cfg = struct ('action', 'type_keys', 'text', text, 'set_text', set_text);
  if (! isempty (title))
    if (isnumeric (title))
      cfg.handle = title;
    else
      cfg.title = title;
    endif
  endif
  r = pywinauto_run (cfg);
  if (! r.ok)
    error ('pywinauto_type_keys: %s', r.error);
  endif
endfunction
