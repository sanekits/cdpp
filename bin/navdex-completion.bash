# navdex-completion.bash
# vim: filetype=sh :

# Recommended: source this from .bashrc

# Requires: you have a ~/bin/navdex-py directory containing navdex_core.py, or
# you set $NAVDEXHOME=[dir] before sourcing navdex-completion.bash

python_ident() {
    for py_candidate in python3.{16..6} python; do
        which "${py_candidate}" &>/dev/null || continue
        (
            pyhome_loc=$("$py_candidate" -c 'import os; print(os.environ.get("HOME"));' 2>/dev/null)
            [[ -z $pyhome_loc ]] && { exit 1; }
            pyhome_nodeid=$(command stat -L "${pyhome_loc}" -c %i)
            home_nodeid=$(command stat -L "${HOME}" -c %i)
            if [[ $pyhome_nodeid != $home_nodeid ]]; then
                # This python isn't native to our shell (e.g. a wsl version from git-bash or vice-versa, etc)
                exit 1
            fi
        ) || continue
        which "$py_candidate"
        return
    done
    echo "ERROR: unable to identify usable python candidate for navdex-completion.bash" >&2
    false
}

export NavdexPython="$(python_ident)"

export NAVDEXHOME=${NAVDEXHOME:-${HOME}/.local/bin/cdpp}


if [[ -f ${NAVDEXHOME}/navdex_core.py ]]; then
    # navdex_core is a python script:

    function navdex_cd_enter {
        local newDir=$1
        # When entering a directory, look for the '.navdex-auto' file:
        if [[ $PWD ==  $newDir ]]; then
            return
        fi
        pushd "$newDir" >/dev/null
        if [[ -f ./.navdex-auto ]]; then
            # Before we source this, we want to figure out if it's a null operation, otherwise we'll
            # print a meaningless sourcing message.
            if [[ $( egrep -v '^#' ./.navdex-auto ) == "" ]]; then
                return  # Yes, there's a .navdex-auto, but it has no initialization logic, it's just comments
            fi
            echo -n "   (navdex sourcing ./.navdex-auto: [" >&2
            source ./.navdex-auto
            echo "] DONE)" >&2
        fi
    }

    function navdex_w {
        # The navdex alias invokes navdex_w: Our job is to pass args to
        # navdex_core.py, and then decide whether we're supposed to change dirs,
        # print the result, or execute the command returned.
        local newDir=$( $NavdexPython $NAVDEXHOME/navdex_core.py "$@" )
        if [[ ! -z $newDir ]]; then
            if [[ "${newDir:0:1}" != "!" ]]; then
                # We're supposed to change to the dir identified:
                #history -s "cd $newDir # to $@"
                navdex_cd_enter "$newDir" "$@"
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
    [[ -f $HOME/.navdex-index ]] || ( touch $HOME/.navdex-index &>/dev/null )
    alias to='set -f;navdex_w'
    alias toa='set -f; navdex_w -a'
    alias tod='set -f; navdex_w -d'
    alias tog='set -f; navdex_w -g'
    alias tor='set -f; navdex_w --report td'

    alias toz='koo() { navdex_debugpy=1 navdex_w "$@"; }; set -f; koo '
    # function toz {
    #     set -f
    #     navdex_debugpy=1 $NavdexPython $NAVDEXHOME/navdex_core.py  "$@"  # Debugger invocation
    #     set +f
    # }

else
	function navdex_w {
		echo "This function only works if \$NAVDEXHOME/navdex_core.py exists."
	}
    alias to=navdex_w
    alias toa=navdex_w
    alias tod=navdex_w
    alias tog=navdex_w
    alias tor=navdex_w
    alias navdex=navdex_w
    alias toz=navdex_w
fi

_navdex()  # Here's our readline completion handler
{
    COMPREPLY=()
    local cur="${COMP_WORDS[COMP_CWORD]}"

    # Extract the path of the index file:
    local navdexfile=$(navdex -q 2>&1 | egrep -m 1 '^Index' | awk '{print $2'})

    local opts="$(egrep -v '^#protect' ${navdexfile} )"

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

#complete -F _navdex navdex
#complete -F _navdex to

