# See https://xon.sh/envvars.html#interactive-prompt

# bottom-toolbar 用の template string。
# `$PROMPT` と同じように設定できる。現状は prompt-toolkit shell でのみ利用可能。
#$BOTTOM_TOOLBAR = ''

# シェル入力のシンタックスハイライトをするかどうかのフラグ。
#$COLOR_INPUT = True

# 結果のシンタックスハイライトをするかどうかのフラグ。
#$COLOR_RESULTS = True

# カレントディレクトリを省略して表示するときに仕様する string 。
#$DYNAMIC_CWD_ELISION_CHAR = ''

# `CWD` プロンプト変数の最大長。文字数か％で表す。
# "20" のとき20文字、 "10%" のとき利用可能な横幅の10%。
#$DYNAMIC_CWD_WIDTH = (float('inf'), 'c')

# Ctrl-D でシェルが終了するのを防ぐ。
$IGNOREEOF = True

# 複数行入力のときのインデント
$INDENT = '    '

# `ls` コマンドと、`$SHELL_TYPE='prompt_toolkit'` の subprocess mode 内でのファイル引数のカラー設定
#$LS_COLORS = '*.7z=1;0;31:*.Z=1;0;31:*.aac=0;36:*.ace=1;0;31:*.alz=1;0;31:*.arc=1;0;31:*.arj=1;0;31:*.asf=1;0;35:*.au=0;36:*.avi=1;0;35:*.bmp=1;0;35:*.bz=1;0;31:*.bz2=1;0;31:*.cab=1;0;31:*.cgm=1;0;35:*.cpio=1;0;31:*.deb=1;0;31:*.dl=1;0;35:*.dwm=1;0;31:*.dz=1;0;31:*.ear=1;0;31:*.emf=1;0;35:*.esd=1;0;31:*.flac=0;36:*.flc=1;0;35:*.fli=1;0;35:*.flv=1;0;35:*.gif=1;0;35:*.gl=1;0;35:*.gz=1;0;31:*.jar=1;0;31:*.jpeg=1;0;35:*.jpg=1;0;35:*.lha=1;0;31:*.lrz=1;0;31:*.lz=1;0;31:*.lz4=1;0;31:*.lzh=1;0;31:*.lzma=1;0;31:*.lzo=1;0;31:*.m2v=1;0;35:*.m4a=0;36:*.m4v=1;0;35:*.mid=0;36:*.midi=0;36:*.mjpeg=1;0;35:*.mjpg=1;0;35:*.mka=0;36:*.mkv=1;0;35:*.mng=1;0;35:*.mov=1;0;35:*.mp3=0;36:*.mp4=1;0;35:*.mp4v=1;0;35:*.mpc=0;36:*.mpeg=1;0;35:*.mpg=1;0;35:*.nuv=1;0;35:*.oga=0;36:*.ogg=0;36:*.ogm=1;0;35:*.ogv=1;0;35:*.ogx=1;0;35:*.opus=0;36:*.pbm=1;0;35:*.pcx=1;0;35:*.pgm=1;0;35:*.png=1;0;35:*.ppm=1;0;35:*.qt=1;0;35:*.ra=0;36:*.rar=1;0;31:*.rm=1;0;35:*.rmvb=1;0;35:*.rpm=1;0;31:*.rz=1;0;31:*.sar=1;0;31:*.spx=0;36:*.svg=1;0;35:*.svgz=1;0;35:*.swm=1;0;31:*.t7z=1;0;31:*.tar=1;0;31:*.taz=1;0;31:*.tbz=1;0;31:*.tbz2=1;0;31:*.tga=1;0;35:*.tgz=1;0;31:*.tif=1;0;35:*.tiff=1;0;35:*.tlz=1;0;31:*.txz=1;0;31:*.tz=1;0;31:*.tzo=1;0;31:*.tzst=1;0;31:*.vob=1;0;35:*.war=1;0;31:*.wav=0;36:*.webm=1;0;35:*.wim=1;0;31:*.wmv=1;0;35:*.xbm=1;0;35:*.xcf=1;0;35:*.xpm=1;0;35:*.xspf=0;36:*.xwd=1;0;35:*.xz=1;0;31:*.yuv=1;0;35:*.z=1;0;31:*.zip=1;0;31:*.zoo=1;0;31:*.zst=1;0;31:bd=40;0;33:ca=0;30;41:cd=40;0;33:di=1;0;34:do=1;0;35:ex=1;0;32:ln=1;0;36:mh=0:mi=0:or=40;0;31:ow=0;34;42:pi=40;0;33:rs=0:sg=0;30;43:so=1;0;35:st=0;37;44:su=0;37;41:tw=0;30;42'

# 入力の2行目以降のプロンプト。str か str を返す function。
$MULTILINE_PROMPT = '>'

# 結果を pritty print するかどうかのフラグ。
#$PRETTY_PRINT_RESULTS = True

# プロンプトテキスト。自動フォーマットされたキーワード引数を含めることができる。
# この値は親プロセスから継承されることはない。
# https://xon.sh/tutorial.html#customizing-the-prompt を参照。
$PROMPT = '{INTENSE_BLUE}{user}{INTENSE_GREEN}@{INTENSE_BLUE}{hostname}{WHITE}:{cwd}\n {RED}{prompt_end}  '

# $PROMPT_FIELDS: `$PROMPT` と `$TITLE` のフォーマットのときに使う変数を保存する辞書。
# https://xon.sh/tutorial.html#customizing-the-prompt を参照。
$PROMPT_FIELDS['env_prefix'] = '['
$PROMPT_FIELDS['env_postfix'] = ']'

# `$PROMPT`, `$RIGHT_PROMPT`, `$BOTTOM_TOOLBAR` を評価、更新する間隔(秒)。デフォルトはゼロで更新しない。
# この変数を有効にするには `$UPDATE_PROMPT_ON_KEYPRESS` を `True` にセットする必要がある。
#$PROMPT_REFRESH_INTERVAL = 0.0

# プロンプトテンプレートのすべてのトークンを受け取る最終プロセッサ。他のトークンの値に基づいて異なるプレフィックスでフォーマットするオプションを提供します。
# powerline テーマのようなものを実装するのに便利。
#$PROMPT_TOKENS_FORMATTER = xonsh.prompt.base.prompt_tokens_formatter_default

# 右側に整列したプロンプトテキスト用の template string。
# `$PROMPT` と同じように設定できる。現状は prompt-toolkit shell でのみ利用可能。
$RIGHT_PROMPT = '{curr_branch} {env_name}'

# どのタイプのシェルを利用するか。現在、2つの基本シェルタイプがサポートされている。
# - `readline` : Python の readline モジュールを利用する。
# - `prompt_toolkit` : prompt_toolkit ライブラリを利用する。
# - `random` : これらの中から起動時にランダムに選択する。
# - `best` : ユーザのシステムで利用可能な中で一番リッチなシェルを選択する。
# `prompt_toolkit` を利用するには prompt_toolkit ライブラリをインストールしておく必要がある。
#$SHELL_TYPE = 'best'

# 無効なコマンドを入力したとき、xonsh が似た有効なコマンドを提案する。
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

