#!/bin/bash

# Running cdpp-version.sh is the correct way to
# get the home path for cdpp and its tools.
CdppVer=0.6.1

set -e

Script=$(readlink -f "$0")
Scriptdir=$(dirname -- "$Script")


if [ -z "$sourceMe" ]; then
    printf "%s\t%s" ${Scriptdir}/cdpp ${CdppVer}
fi
