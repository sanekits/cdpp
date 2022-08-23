#!/bin/bash

# Running cdpp-version.sh is the correct way to
# get the home install path for the tool
KitVersion=0.7.4

canonpath() {
    builtin type -t realpath.sh &>/dev/null && {
        realpath.sh -f "$@"
        return
    }
    builtin type -t readlink &>/dev/null && {
        command readlink -f "$@"
        return
    }
    # Fallback: Ok for rough work only, does not handle some corner cases:
    ( builtin cd -L -- "$(command dirname -- $0)"; builtin echo "$(command pwd -P)/$(command basename -- $0)" )
}

Script=$(canonpath "$0")
Scriptdir=$(dirname -- "$Script")


if [[ -z "$sourceMe" ]]; then
    builtin printf "%s\t%s\n" ${Scriptdir}/cdpp $KitVersion
fi
