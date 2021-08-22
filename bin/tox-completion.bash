# tox-completion.bash
# vim: filetype=sh :

# Recommended: source this from .bashrc

# Requires: you have a ~/bin/tox-py directory containing tox_core.py, or
# you set $TOXHOME=[dir] before sourcing tox-completion.bash

export ToxPython=$(which python3.9 || which python3.8 || which python3.7 || which python3.6 || which python3.5 || which python)
export LmHome=${LmHome:-$HOME}

export TOXHOME=${TOXHOME:-${LmHome}/bin/tox-py}


if [[ -f ${TOXHOME}/tox_core.py ]]; then
    # tox_core is a python script:

    function tox_cd_enter {
        local newDir=$1
        # When entering a directory, look for the '.tox-auto' file:
        if [[ $PWD ==  $newDir ]]; then
            return
        fi
        pushd "$newDir" >/dev/null
        if [[ -f ./.tox-auto ]]; then
            # Before we source this, we want to figure out if it's a null operation, otherwise we'll
            # print a meaningless sourcing message.
            if [[ $( egrep -v '^#' ./.tox-auto ) == "" ]]; then
                return  # Yes, there's a .tox-auto, but it has no initialization logic, it's just comments
            fi
            echo -n "   (tox sourcing ./.tox-auto: [" >&2
            source ./.tox-auto
            echo "] DONE)" >&2
        fi
    }

    function tox_w {
        # The tox alias invokes tox_w: Our job is to pass args to
        # tox_core.py, and then decide whether we're supposed to change dirs,
        # print the result, or execute the command returned.
        local newDir=$( $ToxPython $TOXHOME/tox_core.py "$@" )
        if [[ ! -z $newDir ]]; then
            if [[ "${newDir:0:1}" != "!" ]]; then
                # We're supposed to change to the dir identified:
                tox_cd_enter "$newDir"
            else
                if [[ "${newDir:0:2}" == "!!" ]]; then
                    # A double !! means "run this"
                    eval "${newDir:2}"
                else
                    # A single bang means "print this"
                    echo "${newDir:1}"
                fi
            fi
        fi
        set +f
    }
    [[ -f $HOME/.tox-index ]] || ( touch $HOME/.tox-index &>/dev/null )
    alias to='set -f;tox_w'
    alias toa='set -f; tox_w -a'
    alias tod='set -f; tox_w -d'
    alias tog='set -f; tox_w -g'
    alias tor='set -f; tox_w --report td'
    alias tox='set -f;tox_w'
    alias toz='set -f;tox_debugpy=1 tox_w'
    # function toz {
    #     set -f
    #     tox_debugpy=1 $ToxPython $TOXHOME/tox_core.py  "$@"  # Debugger invocation
    #     set +f
    # }

else
	function tox_w {
		echo "This function only works if \$TOXHOME/tox_core.py exists."
	}
    alias to=tox_w
    alias toa=tox_w
    alias tod=tox_w
    alias tog=tox_w
    alias tor=tox_w
    alias tox=tox_w
    alias toz=tox_w
fi

_tox()  # Here's our readline completion handler
{
    COMPREPLY=()
    local cur="${COMP_WORDS[COMP_CWORD]}"

    # Extract the path of the index file:
    local toxfile=$(tox -q 2>&1 | egrep -m 1 '^Index' | awk '{print $2'})

    local opts="$(egrep -v '^#protect' ${toxfile} )"

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

#complete -F _tox tox
#complete -F _tox to

