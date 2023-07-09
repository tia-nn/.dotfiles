from xonsh.built_ins import XSH
from pathlib import Path
import subprocess
env = XSH.env
home = Path.home()

# see https://xon.sh/envvars.html for details

env['FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE'] = True
env['XONSH_TRACEBACK_LOGFILE'] = str(home / '.xonsh.traceback.log')

# env['AUTO_SUGGEST'] = True
# env['AUTO_SUGGEST_IN_COMPLETION'] = False
# env['MOUSE_SUPPORT'] = False
# env['PROMPT_TOOLKIT_COLOR_DEPTH'] = ''
# env['VI_MODE'] = False
env['XONSH_AUTOPAIR'] = True
# env['XONSH_COPY_ON_DELETE'] = False
env['XONSH_CTRL_BKSP_DELETION'] = True

env['HISTCONTROL'] = 'ignoredups,erasedups'
env['XONSH_HISTORY_BACKEND'] = 'sqlite'

# env['ALIAS_COMPLETIONS_OPTIONS_BY_DEFAULT'] = True
env['CASE_SENSITIVE_COMPLETIONS'] = False

env['COMPLETIONS_CONFIRM'] = False
# env['COMPLETION_MODE'] = 'menu-complete'
# env['UPDATE_COMPLETIONS_ON_KEYPRESS'] = False

env['BASH_COMPLETIONS'] = '~/.dotfiles/xonsh/bash_completions.bash'


# for screenfetch
env['shell_type'] = subprocess.run(
    ('xonsh', '-V'), capture_output=True
).stdout.decode().rstrip()


# warnings.filterwarnings("ignore", category=DeprecationWarning)
