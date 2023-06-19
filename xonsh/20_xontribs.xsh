def _xonshrc_xontribs():
    from typing import List, Union, Optional
    from xonsh.xontribs import xontribs_load, ExitCode


    def load_with_install(package_name: str, xontrib_name: Union[str, List[str]], if_success: Optional[List[str]] = None):
        out, err, code = xontribs_load([xontrib_name])
        if code == ExitCode.NOT_FOUND:
            if ![xpip install @(package_name)]:
                xontribs_load([xontrib_name])
            else:
                return
        if if_success:
            @(if_success)


    load_with_install('xontrib-vox', 'vox')
    load_with_install('xonsh-vox-tabcomplete', 'vox_tabcomplete')
    load_with_install('xontrib-abbrevs', 'abbrevs')
    load_with_install('xontrib-langenv', 'pyenv', ['pyenv', 'shell', '--unset'])=


_xonshrc_xontribs()
