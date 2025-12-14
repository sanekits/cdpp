# cdpp.bashrc - shell init file for cdpp sourced from ~/.bashrc

cdpp-semaphore() {
    [[ 1 -eq  1 ]]
}

[[ -f $HOME/.local/bin/cdpp/cdx.bashrc ]] && {
    source $HOME/.local/bin/cdpp/cdx.bashrc
}

cdpp_help() {
    cat <<EOF
cdpp enhances the bash 'cd' command with more flexibility and efficiency.
Provides:
--------------
cd            Wraps the built-in 'cd' command
to            Extended dir-change tool using disk indexes (has it's own --help)
.-            Return to previous dir (alias)
.p            Invoke 'popd' (alias)
.3            Go up 3 levels in tree (alias)
cdpath        Print current \$CDPATH value
cdpath_add    Add one or more dirs to CDPATH, default is PWD
cdpath_reset  Restore shell-init value of \$CDPATH
cdpp          Admin tool:
    --help, --version
cd --mark|-m,
    cdmark    Mark current dir in bash history
~/.cdpprc     Init file: see this for CDPATH guidance
dirs          Wraps builtin dirs to provide menu go-to
EOF
}

cdmark() {
    [[ $# -eq 0 ]] && set -- $PWD
    for xdir; do
        local xm="cd $(readlink -f ${xdir}) # cdmark"
        builtin history -s "$xm"
        echo "$xm"
    done
}

cd() {
    [[ $# == 0 ]] && { builtin cd; return; }
    local use_pushd=true
    [[ $1 =~ ^(-m)|(--mark)$ ]] && { shift; cdmark "$@" ; return; }
    [[ -d "$1" && "$1" != */* ]] && use_pushd=false
    [[ "$1" =~ (\.\..*)|(.*\-[LPe@]+) ]] && use_pushd=false
    [[ $1 == --help ]] && { cdpp --help; return; }
    ( builtin cd "$@" &> /dev/null ) && {
        $use_pushd && builtin pushd "$@" >/dev/null || builtin cd "$@";
    }
    [[ $? == 0 ]] && return;
    set -f; navdex_w "$@"
}

cdpath() {
    echo "CDPATH=$CDPATH"
}

cdpath_add() {
    local new_path=
    while true; do
        new_path="$1"
        [[ -z $new_path ]] && new_path=$PWD;
        for pp in $(echo "$CDPATH" | tr ':' ' ');
        do
            [[ "$pp" == "${new_path}" ]] && {
                # We already have this path:
                [[ -z $2 ]] && break 2;
                shift && continue 2;
            }
        done;
        CDPATH="${CDPATH}:${new_path}"
        shift
        [[ -z $1 ]] && break
    done
    cdpath
}

cdpath_reset() {
    CDPATH="${CDPATH_INIT}"
    cdpath
}



dirs() {
    local pick; local dd
    [[ ${#1} == 1 && $1 != - ]] && { pick=$1; shift; }
    [[ $# -gt -0 || $1 == -* ]] && { builtin dirs "$@"; return; }
    set -- $( IFS=$'\n'; builtin dirs |  command tr ' ' '\n' | command sed -e "s@\~@$HOME@" | sort -u )

    keys=( {0..9} {a..p} {r..z} {A..P} {R..Z} )

    if [[ -z $pick ]]; then
        local ndx=-1
        for dd;  do
            (( ndx++ ))
            echo -en "${dd} \033[;31m${keys[$ndx]}"
            [[ $dd == '~' ]] && dd=$HOME
            [[ ${dd} == ${PWD} ]] && builtin echo -en "\033[;32m <-- cwd"
            builtin echo -e "\033[;0m"
        done
    fi

    local vkeys="${keys[@]}"
    vkeys=${vkeys// }  # Remove spaces

    local vdirs=( $@ )
    while true; do
        if [[ -n $pick ]]; then
            selection=$pick
        else
            builtin read -n 1 -p ":: Select target dir: " selection
        fi
        [[ -z $selection ]] && return
        [[ $selection =~ [qQ] ]] && return
        local prefix="${vkeys%${selection}*}"
        local pos="${#prefix}"
        [[ $pos -ge  ${#vdirs[@]} ]] && { pick=; builtin echo; continue; }
        xdir=${vdirs[$pos]}
        [[ $xdir == '~' ]] && xdir=$HOME
        builtin pushd $xdir &>/dev/null && { builtin history -s "cd $xdir"; return; }
    done
}

cdpp() {
    [[ $# -eq 0 ]] && { cdpp_help; return; }
    while [[ -n $1 ]]; do
        case $1 in
            -h|--help)
                cdpp_help
                return
                ;;
            -v|--version)
                cdpp-version.sh
                return
                ;;
            *)
                echo "Unknown argument: $1.  Just use 'cd' if you're trying to change directories."
                false; return
                ;;
        esac
        shift
    done
}

cd_execute() {
    # change directory and then run a commmand.
    # The first arg is interpreted by the cd() function above, and then subsequent
    # arguments are evaluated after the directory change completes.
    [[ $# -lt 2 ]] && {
        case $1 in
            -h|--help) echo "cd_execute [dir-arg] [command...[args] # Change directory and then evaluate remaining command" ;;
            *)  echo "Unknown arg(s): $@" >&2;;
        esac
        false;
        return;
    }
    local cd_to_arg="$1"; shift;
    cd "${cd_to_arg}" && {
        eval "$@"
    }
}

alias cdex='cd_execute'


[[ -f $HOME/.cdpprc ]] && source ${HOME}/.cdpprc
export NAVDEXHOME=${HOME}/.local/bin/cdpp
[[ $UID == 0 && -z $USER ]] && export USER=root
[[ -f $HOME/.local/bin/cdpp/navdex-completion.bash ]] && {
    source $HOME/.local/bin/cdpp/navdex-completion.bash
}

true

