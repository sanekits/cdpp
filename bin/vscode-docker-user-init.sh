#!/bin/bash
# vscode-docker-user-init.sh
# Invoked when vscode builds the dev container, our job is to improve the 'vscode' user environment

Script=$(readlink -f $0)

cat >> /home/vscode/.bashrc <<-EOF
alias lr='ls -lirta'
set -o vi
PATH=\$PATH:/host_home/bin
[[ -f /host_home/bin/git.bashrc ]] && {
    source /host_home/bin/git.bashrc
    initGitStuff
}
[[ -f ~/.vshinit ]] || {
    echo "Your dotfiles were zapped by ${Script} during container build"
    touch ~/.vshinit
}
EOF

