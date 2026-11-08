def _xonshrc_make_logfile():
    import warnings
    from pathlib import Path

    from xonsh.built_ins import XSH

    from xontrib.dotfiles._warnings import AutoInitializedWarning

    logfile = XSH.env.get('XONSH_TRACEBACK_LOGFILE')
    if logfile is None:
        return

    path = Path(logfile)
    if path.is_dir():
        warnings.warn(f'$XONSH_TRACEBACK_LOGFILE ({path}) is directory. Use {path / "log.txt"}',
                      AutoInitializedWarning)
        path = path / 'log.txt'
        XSH.env['XONSH_TRACEBACK_LOGFILE'] = str(path)

    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


_xonshrc_make_logfile()
