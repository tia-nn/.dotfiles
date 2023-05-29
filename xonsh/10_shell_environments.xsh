# see https://xon.sh/envvars.html for details

$FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE = True
$XONSH_TRACEBACK_LOGFILE = p'~/.xonsh.traceback.log'

#$AUTO_SUGGEST = True
#$AUTO_SUGGEST_IN_COMPLETION = False
#$MOUSE_SUPPORT = False
#$PROMPT_TOOLKIT_COLOR_DEPTH = ''
#$VI_MODE = False
$XONSH_AUTOPAIR = True
#$XONSH_COPY_ON_DELETE = False
$XONSH_CTRL_BKSP_DELETION = True

$HISTCONTROL = 'ignoredups,erasedups'
$XONSH_HISTORY_BACKEND = 'sqlite'

# $ALIAS_COMPLETIONS_OPTIONS_BY_DEFAULT = True
$CASE_SENSITIVE_COMPLETIONS = False

$COMPLETIONS_CONFIRM = False
# $COMPLETION_MODE = 'menu-complete'
# $UPDATE_COMPLETIONS_ON_KEYPRESS = False

$BASH_COMPLETIONS = '~/.dotfiles/xonsh/bash_completions.bash'


# for screenfetch
$shell_type = $(xonsh -V).strip()



# warnings.filterwarnings("ignore", category=DeprecationWarning)
