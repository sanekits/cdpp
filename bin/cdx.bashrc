# :vim filetype=sh:
# cdx() enhances 'cd' by maintaining a cache of dirs visited (in DIRSTACK) and
# presenting them as a selectable list if the user provides no argument.
#
cdx ()
{
    [[ $# == 0 ]] && {
        _cdselect
        return
    };
    case "$@" in
        -h|--help)
            builtin help cd
            echo "cdx: [dir]"
            echo "  Present selection of cached dirs for dir change"
            echo "  [dir]: change to dir and add it to cache"
            return ;;
    esac
    _cdview -k | command grep -Eq "^${PWD}\$" || {
        builtin pushd -n "$PWD" > /dev/null
    }
    builtin cd "$@" || return
    _cdview -k | command grep -Eq "^${PWD}\$" || {
        builtin pushd -n "$PWD" > /dev/null
    }
    true
}

[[ $(type -t _cd) == function ]] && {
    complete -o nospace -F _cd cdx
}

_cdview() {
    builtin printf "%s\n" "${DIRSTACK[@]}" | (
        case $1 in
            -u) cat | command sort -u ;;
            -k) cat |  command tail -n +2 | command sort -u ;;
            *) cat
        esac
    )
}

_cdselect() {
    select xdir in $(_cdview -k); do
        builtin cd "$xdir"
        return
    done
}

alias .1='builtin cd ..'
alias .2='builtin pushd ../.. &>/dev/null'
alias .3='builtin pushd ../../.. &>/dev/null'
alias .4='builtin pushd ../../../.. &>/dev/null'
alias .5='builtin pushd ../../../../.. &>/dev/null'
alias .6='builtin pushd ../../../../../.. &>/dev/null'

