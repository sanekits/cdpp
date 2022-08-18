#!/bin/bash
# cdpp.sh
#  This script can be removed if you don't need it -- and if you do
# that you should remove the entry from _symlinks_ and make-kit.mk also.

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

scriptName="$(canonpath "$0")"
scriptDir=$(command dirname -- "${scriptName}")

die() {
    builtin echo "ERROR($(command basename -- ${scriptName})): $*" >&2
    builtin exit 1
}

stub() {
   builtin echo "  <<< STUB[$*] >>> " >&2
}
main() {
    builtin echo "Hello cdpp, shellkit edition: args:[$*]"
}

[[ -z ${sourceMe} ]] && {
    main "$@"
    exit
}
true
