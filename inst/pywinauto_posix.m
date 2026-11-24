## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
## Internal helper: MSYS2 Python (shipped with Octave) expects POSIX paths.
function p = pywinauto_posix (p)
  p = strrep (p, '\', '/');
  if (numel (p) >= 3 && p(2) == ':')
    d = p(1);
    if (d >= 'A' && d <= 'Z')
      d = char (double (d) + 32);
    endif
    p = ['/' d p(3:end)];
  endif
endfunction
