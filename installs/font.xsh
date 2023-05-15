mkdir -p ~/.dotfiles/font/tool

# 源ノ角ゴシック Code https://github.com/adobe-fonts/source-han-code-jp/releases/tag/2.012R
wget "https://github.com/adobe-fonts/source-han-code-jp/releases/download/2.012R/SourceHanCodeJP.ttc" \
    -O ~/.dotfiles/font/SourceHanCodeJP.ttc

docker run --rm -v ${HOME}/.dotfiles/font:/in -v ${HOME}/.dotfiles/font/out:/out nerdfonts/patcher /in/SourceHanCodeJP.ttc
