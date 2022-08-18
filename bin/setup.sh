#!/bin/bash
# setup.sh for cdpp
#  This script is run from a temp dir after the self-install code has
# extracted the install files.   The default behavior is provided
# by the main_base() call, but after that you can add your own logic
# and installation steps.

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

stub() {
   builtin echo "  <<< STUB[$*] >>> " >&2
}
scriptName="$(canonpath  $0)"
scriptDir=$(command dirname -- "${scriptName}")

source ${scriptDir}/shellkit/setup-base.sh

die() {
    builtin echo "ERROR(setup.sh): $*" >&2
    builtin exit 1
}

main() {
    Script=${scriptName} main_base "$@"
    builtin cd ${HOME}/.local/bin || die 208
    # TODO: kit-specific steps can be added here
}

[[ -z ${sourceMe} ]] && {
    main "$@"
    builtin exit
}
command true
