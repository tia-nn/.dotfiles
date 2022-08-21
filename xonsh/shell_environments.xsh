# see https://xon.sh/envvars.html for details

#$XONSH_COLOR_STYLE = 'default'
$FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE = True
$XONSH_TRACEBACK_LOGFILE = $HOME + '/.xonsh.traceback.log'

#$BOTTOM_TOOLBAR = ''
#$COLOR_INPUT = True
#$COLOR_RESULTS = True
#$DYNAMIC_CWD_ELISION_CHAR = ''
#$DYNAMIC_CWD_WIDTH = (float('inf'), 'c')
$IGNOREEOF = True
$INDENT = '    '
#$LS_COLORS = '*.7z=1;0;31:*.Z=1;0;31:*.aac=0;36:*.ace=1;0;31:*.alz=1;0;31:*.arc=1;0;31:*.arj=1;0;31:*.asf=1;0;35:*.au=0;36:*.avi=1;0;35:*.bmp=1;0;35:*.bz=1;0;31:*.bz2=1;0;31:*.cab=1;0;31:*.cgm=1;0;35:*.cpio=1;0;31:*.deb=1;0;31:*.dl=1;0;35:*.dwm=1;0;31:*.dz=1;0;31:*.ear=1;0;31:*.emf=1;0;35:*.esd=1;0;31:*.flac=0;36:*.flc=1;0;35:*.fli=1;0;35:*.flv=1;0;35:*.gif=1;0;35:*.gl=1;0;35:*.gz=1;0;31:*.jar=1;0;31:*.jpeg=1;0;35:*.jpg=1;0;35:*.lha=1;0;31:*.lrz=1;0;31:*.lz=1;0;31:*.lz4=1;0;31:*.lzh=1;0;31:*.lzma=1;0;31:*.lzo=1;0;31:*.m2v=1;0;35:*.m4a=0;36:*.m4v=1;0;35:*.mid=0;36:*.midi=0;36:*.mjpeg=1;0;35:*.mjpg=1;0;35:*.mka=0;36:*.mkv=1;0;35:*.mng=1;0;35:*.mov=1;0;35:*.mp3=0;36:*.mp4=1;0;35:*.mp4v=1;0;35:*.mpc=0;36:*.mpeg=1;0;35:*.mpg=1;0;35:*.nuv=1;0;35:*.oga=0;36:*.ogg=0;36:*.ogm=1;0;35:*.ogv=1;0;35:*.ogx=1;0;35:*.opus=0;36:*.pbm=1;0;35:*.pcx=1;0;35:*.pgm=1;0;35:*.png=1;0;35:*.ppm=1;0;35:*.qt=1;0;35:*.ra=0;36:*.rar=1;0;31:*.rm=1;0;35:*.rmvb=1;0;35:*.rpm=1;0;31:*.rz=1;0;31:*.sar=1;0;31:*.spx=0;36:*.svg=1;0;35:*.svgz=1;0;35:*.swm=1;0;31:*.t7z=1;0;31:*.tar=1;0;31:*.taz=1;0;31:*.tbz=1;0;31:*.tbz2=1;0;31:*.tga=1;0;35:*.tgz=1;0;31:*.tif=1;0;35:*.tiff=1;0;35:*.tlz=1;0;31:*.txz=1;0;31:*.tz=1;0;31:*.tzo=1;0;31:*.tzst=1;0;31:*.vob=1;0;35:*.war=1;0;31:*.wav=0;36:*.webm=1;0;35:*.wim=1;0;31:*.wmv=1;0;35:*.xbm=1;0;35:*.xcf=1;0;35:*.xpm=1;0;35:*.xspf=0;36:*.xwd=1;0;35:*.xz=1;0;31:*.yuv=1;0;35:*.z=1;0;31:*.zip=1;0;31:*.zoo=1;0;31:*.zst=1;0;31:bd=40;0;33:ca=0;30;41:cd=40;0;33:di=1;0;34:do=1;0;35:ex=1;0;32:ln=1;0;36:mh=0:mi=0:or=40;0;31:ow=0;34;42:pi=40;0;33:rs=0:sg=0;30;43:so=1;0;35:st=0;37;44:su=0;37;41:tw=0;30;42'
$MULTILINE_PROMPT = '>'
#$PRETTY_PRINT_RESULTS = True

# see https://xon.sh/tutorial.html#customizing-the-prompt for details
$PROMPT = '{INTENSE_BLUE}{user}{INTENSE_GREEN}@{INTENSE_BLUE}{hostname}{WHITE}:{cwd}\n {RED}{prompt_end}  '
$RIGHT_PROMPT = '{curr_branch} {env_name}'
# PROMPT_FIELDS
$PROMPT_FIELDS['env_prefix'] = '['
$PROMPT_FIELDS['env_postfix'] = ']'
#$PROMPT_TOKENS_FORMATTER = xonsh.prompt.base.prompt_tokens_formatter_default
#$SHELL_TYPE = 'best'
$SUGGEST_COMMANDS = False
#$SUGGEST_MAX_NUM = 5
#$SUGGEST_THRESHOLD = 3
$SUPPRESS_BRANCH_TIMEOUT_MESSAGE = True
#$TITLE = xonsh.environ.DEFAULT_TITLE
#$UPDATE_PROMPT_ON_KEYPRESS = False
#$VC_BRANCH_TIMEOUT = 0.1
#$VC_GIT_INCLUDE_UNTRACKED = False
$VC_HG_SHOW_BRANCH = False
$XONSH_HISTORY_MATCH_ANYWHERE = True
#$XONSH_STDERR_POSTFIX = ''
#$XONSH_STDERR_PREFIX = ''

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
