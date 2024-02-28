def _xonshrc_make_logfile():
    import warnings
    from os.path import sep, isdir, isfile

    from lib.xonshrc_warnings import AutoInitializedWarning


    # https://github.com/xonsh/xonsh/issues/5166
    XONSH_TRACEBACK_LOGFILE = $XONSH_TRACEBACK_LOGFILE
    if XONSH_TRACEBACK_LOGFILE is None:
        pass
    elif isdir(XONSH_TRACEBACK_LOGFILE):
        warnings.warn(f'XONSH_TRACEBACK_LOGFILE ({XONSH_TRACEBACK_LOGFILE}) is directory. Use {XONSH_TRACEBACK_LOGFILE}{sep}log.txt', AutoInitializedWarning)
        XONSH_TRACEBACK_LOGFILE = XONSH_TRACEBACK_LOGFILE + sep + 'log.txt'
        touch XONSH_TRACEBACK_LOGFILE
    elif not isfile(XONSH_TRACEBACK_LOGFILE):
        warnings.warn(f'Make traceback log file to {XONSH_TRACEBACK_LOGFILE}', AutoInitializedWarning)
        touch XONSH_TRACEBACK_LOGFILE


_xonshrc_make_logfile()
