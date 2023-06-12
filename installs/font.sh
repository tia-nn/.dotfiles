#!/bin/sh

mkdir -p ~/.dotfiles/font/tool

# 源ノ角ゴシック Code https://github.com/adobe-fonts/source-han-code-jp/releases/tag/2.012R
wget "https://github.com/adobe-fonts/source-han-code-jp/releases/download/2.012R/SourceHanCodeJP.ttc" \
    -O ~/.dotfiles/font/SourceHanCodeJP.ttc

# NerdFonts Symbols Only https://github.com/ryanoasis/nerd-fonts/releases
# see also https://www.nerdfonts.com/cheat-sheet
wget "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.1/NerdFontsSymbolsOnly.zip" \
    -O ~/.dotfiles/font/NerdFontsSymbolsOnly.zip
unzip ~/.dotfiles/font/NerdFontsSymbolsOnly.zip -d ~/.dotfiles/font/NerdFontsSymbolsOnly
cp ~/.dotfiles/font/NerdFontsSymbolsOnly/*.ttf ~/.dotfiles/font
