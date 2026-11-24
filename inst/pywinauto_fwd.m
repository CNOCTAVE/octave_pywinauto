## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
## Internal helper: Windows paths must be forward-slashed for Python.
function p = pywinauto_fwd (p)
  p = strrep (p, '\', '/');
endfunction
