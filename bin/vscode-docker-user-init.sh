#!/bin/bash
# vscode-docker-user-init.sh
# Invoked when vscode builds the dev container, our job is to improve the 'vscode' user environment

die() {
    echo "ERROR: $*" >&2
    exit 1
}

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

mkdir ~/bb-cert && cd ~/bb-cert && ln -sf /home/lmatheson4/bb-cert/bloomberg-root-ca.crt ./Bloomberg_LP_CORP_CLASS_1_ROOT_G2.pem || die 101

