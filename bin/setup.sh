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
    #grep -q "Added by cdpp-setup.sh" ${HOME}/.bashrc 2>/dev/null && return
    [[ -f ${HOME}/.cdpprc ]] || cp ${HOME}/.local/bin/cdpp/cdpprc ${HOME}/.cdpprc
    local vk=$( /bin/bash -ic 'type -t cdpp 2>/dev/null' )
    if [[ $vk == *function ]]; then
        return
    fi

    (
        echo '[[ -n $PS1 && -f ${HOME}/.local/bin/cdpp/cdpp ]] && source ${HOME}/.local/bin/cdpp/cdpp # Added by cdpp-setup.sh'
        echo
    ) >> ${HOME}/.bashrc
    reload_reqd=true
}


main() {
    reload_reqd=false
    if [[ ! -d $HOME/.local/bin/cdpp ]]; then
        command mkdir -p $HOME/.local/bin/cdpp || die "Failed creating $HOME/.local/bin/cdpp"
    fi
    if [[ $(inode $Script) -eq $(inode ${HOME}/.local/bin/cdpp/setup.sh) ]]; then
        die "cannot run setup.sh from ${HOME}/.local/bin"
    fi
    builtin cd ${HOME}/.local/bin/cdpp || die "101"
    command rm -rf ./* || die "102"
    command cp -r ${Scriptdir}/* ./ || die "failed copying from ${Scriptdir} to $PWD"
    builtin cd .. # Now we're in .local/bin
    command ln -sf ./cdpp/cdpp-version.sh ./
    path_fixup "$PWD" || die "102"
    shrc_fixup || die "104"
    $reload_reqd && builtin echo "Shell reload required ('bash -l')" >&2
}

[[ -z $sourceMe ]] && main "$@"
