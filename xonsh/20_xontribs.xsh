from typing import List, Union

xontrib load vox

def load_with_install(package_name: str, xontrib_name: Union[str, List[str]]):
    if not ![xontrib load @(xontrib_name)]:
        xpip install @(package_name) and \
        xontrib load @(xontrib_name)

load_with_install('xonsh-vox-tabcomplete', 'vox_tabcomplete')
load_with_install('xontrib-abbrevs', 'abbrevs')
load_with_install('xontrib-langenv', ['pyenv'])
pyenv shell --unset
