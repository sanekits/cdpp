# /workspace/user.bashrc -> ~/.bashrc

# User specific aliases and functions

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

set -o vi
alias lr='ls -lirta'
PS1="\[\e[1;33m\]\D{%b-%d %H:%M:%S}\[\e[0m\] \[\e[1;35m\]\w\[\e[0m\] [cdx-development]
\[\e[1;36m\][\u Wsl2 \h]\[\e[0m\]\[[01;32m\]Γ£ô\[[;0m\]> "

source /opt/bb/share/bash-completion/bash_completion
source /workspace/cdx.bashrc
