#!/bin/bash

# Running cdpp-version.sh is the correct way to
# get the home install path for the tool
KitVersion=1.0.2

# The shellkit/ tooling naturally evolves out from under the dependent kits.  ShellkitSetupVers allows
# detecting the need for refresh of templates/* derived files.  To bump the root version, 
# zap all templates/* containing 'ShellkitTemplateVers' constants and changes to the corresponding dependent kits
# Note that within templates/* there may be diverse versions in upstream shellkit, they don't all have to match,
# but the derived copies should be sync'ed with upstream as needed.
#shellcheck disable=2034
ShellkitTemplateVers=2

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
    ( builtin cd -L -- "$(command dirname -- "$0")" || exit; builtin echo "$(command pwd -P)/$(command basename -- "$0")" )
}

Script=$(canonpath "$0")
Scriptdir=$(dirname -- "$Script")


if [[ -z "$sourceMe" ]]; then
    builtin printf "%s\t%s\n" "${Scriptdir}" $KitVersion
fi
