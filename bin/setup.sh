#!/bin/bash
# setup.sh for cdpp

die() {
    echo "ERROR: $@" >&2
    exit 1
}

canonpath() {
    ( cd -L -- "$(dirname -- $0)"; echo "$(pwd -P)/$(basename -- $0)" )
}

Script=$(canonpath "$0")
Scriptdir=$(dirname -- "$Script")
inode() {
    ( command ls -i "$1" | command awk '{print $1}') 2>/dev/null
}

is_on_path() {
    local tgt_dir="$1"
    [[ -z $tgt_dir ]] && { true; return; }
    local vv=( $(echo "${PATH}" | tr ':' '\n') )
    for v in ${vv[@]}; do
        if [[ $tgt_dir == $v ]]; then
            return
        fi
    done
    false
}

path_fixup() {
    # Add ~/.local/bin to the PATH if it's not already.  Modify
    # either .bash_profile or .profile honoring bash startup rules.
    local tgt_dir="$1"
    if is_on_path "${tgt_dir}"; then
        return
    fi
    local profile=$HOME/.bash_profile
    [[ -f $profile ]] || profile=$HOME/.profile
    echo 'export PATH=$HOME/.local/bin:$PATH # Added by cdpp-setup.sh' >> ${profile} || die 202
    echo "~/.local/bin added to your PATH." >&2
    reload_reqd=true
}

shrc_fixup() {
    # We must ensure that .bashrc sources our cdpp script
    local tgt_dir="$1"
    [[ $(type -t cdpp) == 'function' ]] && return

    (
        echo '[[ -n $PS1 && ' "-f ${tgt_dir}/cdpp/cdpp" ' ]] && source ' "${tgt_dir}/cdpp/cdpp" ' # Added by cdpp-setup.sh'
        echo
    ) >> ${HOME}/.bashrc
    echo "Your .bashrc has been updated." >&2
    reload_reqd=true
}


main() {
    reload_reqd=false
    if [[ ! -d $HOME/.local/bin/cdpp ]]; then
        mkdir -p $HOME/.local/bin/cdpp || die "Failed creating $HOME/.local/bin/cdpp"
    fi
    if [[ $(inode $Script) -eq $(inode ${HOME}/.local/bin/cdpp/setup.sh) ]]; then
        die "cannot run setup.sh from ${HOME}/.local/bin"
    fi
    cd ${HOME}/.local/bin/cdpp || die "101"
    rm -rf ./* || die "102"
    cp -r ${Scriptdir}/* ./ || die "failed copying from ${Scriptdir} to $PWD"
    cd .. # Now we're in .local/bin
    path_fixup "$PWD" || die "102"
    shrc_fixup "$PWD" || die "104"
    $reload_reqd && echo "Shell reload required ('bash -l')" >&2
}

[[ -z $sourceMe ]] && main "$@"
