#!/bin/bash
# vscode-docker-user-init.sh
# Invoked when vscode builds the dev container, our job is to improve the 'vscode' user environment

Script=$(readlink -f $0)

cat >> /home/vscode/.bashrc <<-EOF
alias lr='ls -lirta'
alias gs='git status'
set -o vi
[[ -f ~/.vshinit ]] || {
    echo "Your dotfiles were zapped by ${Script} during container build"
    touch ~/.vshinit
}
EOF

