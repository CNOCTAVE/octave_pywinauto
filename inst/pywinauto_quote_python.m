## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
## Internal helper: quote a python command for system().
function q = pywinauto_quote_python (py)
  if (! isempty (regexp (py, '\.exe$', 'once')))
    q = ['"' py '"'];
  elseif (isempty (strfind (py, ' ')))
    q = ['"' py '"'];
  else
    q = py;
  endif
endfunction
