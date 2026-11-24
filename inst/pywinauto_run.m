## Copyright (C) 2026 Yu Hongbo <yuhongbo@member.fsf.org>, CNOCTAVE
## SPDX-License-Identifier: GPL-3.0-or-later
##
## -*- texinfo -*-
## @deftypefn {} {@var{res} =} pywinauto_run (@var{cfg})
## Perform one pywinauto action.  @var{cfg} must contain @code{action};
## supported actions are version, windows, start, connect, click, type_keys,
## close and texts.  Returns a struct with @code{ok}, @code{backend} and
## action-specific fields.
## @end deftypefn
function res = pywinauto_run (cfg)
  if (nargin < 1 || ! isstruct (cfg))
    print_usage ();
  endif
  ctx = pywinauto_init ();

  base = tempname ();
  cfg_file = [base '_cfg.json'];
  res_file = [base '_res.json'];
  driver_arg = pywinauto_fwd (ctx.driver);
  cfg_arg = pywinauto_fwd (cfg_file);
  res_arg = pywinauto_fwd (res_file);
  if (ctx.posix_paths)
    driver_arg = pywinauto_posix (ctx.driver);
    cfg_arg = pywinauto_posix (cfg_file);
    res_arg = pywinauto_posix (res_file);
  endif
  cfg.result_file = res_arg;

  fid = fopen (cfg_file, 'w');
  if (fid == -1)
    error ('pywinauto_run: cannot write temporary config');
  endif
  fwrite (fid, jsonencode (cfg));
  fclose (fid);

  pyq = pywinauto_quote_python (ctx.python);
  cmd = sprintf ('%s "%s" "%s"', pyq, driver_arg, cfg_arg);
  [st, out] = system (cmd);

  res = struct ('ok', false, 'backend', ctx.backend, 'error', out);
  if (! isempty (dir (res_file)))
    try
      res = jsondecode (fileread (res_file));
    catch
      res.error = out;
    end_try_catch
  endif
endfunction
