cdx ()
{
    [[ $# == 0 ]] && {
        _cdselect
        return
    };
    [[ "$@" == *-h* ]] && {
        builtin help cd
        echo "cdx [dir]  #  Change to given dir and add it to cache"
        echo "cdx  #  Select a dir from cache"
        return
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
    case $1 in
        -u) builtin printf "%s\n" "${DIRSTACK[@]}" | command sort -u ;;
        -k) builtin printf "%s\n" "${DIRSTACK[@]}" |  command tail -n +2 | command sort -u ;;
        *) builtin printf "%s\n" "${DIRSTACK[@]}"
    esac
}

_cdselect() {
    select xdir in $(_cdview -u); do
        builtin cd "$xdir"
        return
    done
}

alias .1='builtin cd ..'
alias .2='builtin cd ../..'
alias .3='builtin cd ../../..'
alias .4='builtin cd ../../../..'

