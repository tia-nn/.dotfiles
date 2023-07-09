def _xonshrc_xontribs():
    from typing import List, Union, Optional
    from xonsh.xontribs import xontribs_load, ExitCode
    from xonsh.built_ins import XSH
    import subprocess

    def load_with_install(package_name: str, xontrib_name: Union[str, List[str]]):
        out, err, code = xontribs_load([xontrib_name])
        if code == ExitCode.NOT_FOUND:
            if subprocess.run(XSH.aliases['xpip'] + ['install', package_name], capture_output=True).returncode == 0:
                xontribs_load([xontrib_name])
            else:
                return

    load_with_install('xontrib-vox', 'vox')
    load_with_install('xonsh-vox-tabcomplete', 'vox_tabcomplete')
    load_with_install('xontrib-abbrevs', 'abbrevs')
    # load_with_install('xontrib-langenv', 'pyenv', ['pyenv', 'shell', '--unset'])


_xonshrc_xontribs()
