import xonsh
from xonsh.built_ins import XSH

from lib.paths import state_dir, xonsh_dir

env = XSH.env

# see https://xon.sh/envvars.html for details

env['FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE'] = True
# 置き場所のディレクトリがないと、xonsh は黙って None にしてしまうので先に作る
state_dir().mkdir(parents=True, exist_ok=True)
env['XONSH_TRACEBACK_LOGFILE'] = str(state_dir() / 'traceback.log')

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

env['BASH_COMPLETIONS'] = str(xonsh_dir() / 'bash_completions.bash')


# for screenfetch（`xonsh -V` と同じ形。起動のたびに xonsh を実行しないよう、バージョンから作る）
env['shell_type'] = f'xonsh/{xonsh.__version__}'


# warnings.filterwarnings("ignore", category=DeprecationWarning)
