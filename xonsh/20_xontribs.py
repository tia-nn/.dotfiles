def _xonshrc_xontribs():
    from xonsh.xontribs import xontribs_load, ExitCode
    import subprocess

    from lib.typing_builtins import aliases


    def load_with_install(package_name: str, xontrib_name: str):
        out, err, code = xontribs_load([xontrib_name])
        if code == ExitCode.NOT_FOUND:
            if subprocess.run(aliases['xpip'] + ['install', package_name], capture_output=True).returncode == 0:
                xontribs_load([xontrib_name])
            else:
                return


    load_with_install('xontrib-vox', 'vox')
    load_with_install('xonsh-vox-tabcomplete', 'vox_tabcomplete')
    load_with_install('xontrib-abbrevs', 'abbrevs')
    load_with_install('xonsh-direnv', 'direnv')
    # load_with_install('xontrib-langenv', 'pyenv', ['pyenv', 'shell', '--unset'])


_xonshrc_xontribs()
