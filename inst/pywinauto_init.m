## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {@var{ctx} =} pywinauto_init ()
## Locate a Windows Python that can load the vendored pywinauto bytecode and
## return a context struct.  Octave's built-in CPython 3.12 uses the bundled
## ctypes Win32 backend; a normal CPython with pywin32 uses real pywinauto.
## @end deftypefn
function ctx = pywinauto_init ()
  persistent cached
  if (! isempty (cached))
    ctx = cached;
    return;
  endif

  here = fileparts (which ('pywinauto_init'));
  driver = fullfile (here, 'pywinauto_driver.py');
  if (isempty (dir (driver)))
    error ('pywinauto_init: pywinauto_driver.py not found');
  endif
  if (! ispc ())
    error ('pywinauto_init: octave_pywinauto supports Windows only');
  endif

  candidates = {};
  envpy = getenv ('PYWINAUTO_PYTHON');
  if (! isempty (envpy))
    candidates{end+1} = envpy;
  endif
  candidates{end+1} = 'python3';
  candidates{end+1} = 'python';
  candidates{end+1} = 'py -3';
  oh = getenv ('OCTAVE_HOME');
  if (! isempty (oh))
    candidates{end+1} = fullfile (oh, 'usr', 'bin', 'python.exe');
  endif

  ctx = struct ('python', '', 'driver', driver, 'backend', '', 'posix_paths', false);
  for i = 1:numel (candidates)
    py = candidates{i};
    pyq = pywinauto_quote_python (py);
    [st2, exeout] = system (sprintf ('%s -c "import sys; print(sys.executable)"', pyq));
    posix = ! isempty (regexp (exeout, '^/usr/', 'once')) || ! isempty (regexp (exeout, 'Octave', 'once'));
    base = tempname ();
    cfg = [base '_cfg.json'];
    res = [base '_res.json'];
    res_arg = res;
    driver_arg = driver;
    cfg_arg = cfg;
    if (posix)
      res_arg = pywinauto_posix (res);
      driver_arg = pywinauto_posix (driver);
      cfg_arg = pywinauto_posix (cfg);
    endif
    cfgobj = struct ('action', 'version', 'result_file', res_arg);
    fid = fopen (cfg, 'w');
    if (fid == -1)
      continue;
    endif
    fwrite (fid, jsonencode (cfgobj));
    fclose (fid);
    cmd = sprintf ('%s "%s" "%s"', pyq, driver_arg, cfg_arg);
    [st, out] = system (cmd);
    if (st == 0 && ! isempty (dir (res)))
      try
        info = jsondecode (fileread (res));
      catch
        info = struct ('ok', false);
      end_try_catch
      if (isfield (info, 'ok') && info.ok)
        ctx.python = py;
        ctx.backend = info.backend;
        ctx.posix_paths = posix;
        break;
      endif
    endif
  endfor

  if (isempty (ctx.python))
    error ('pywinauto_init: no Windows Python with pywinauto found; set PYWINAUTO_PYTHON');
  endif
  cached = ctx;
endfunction
