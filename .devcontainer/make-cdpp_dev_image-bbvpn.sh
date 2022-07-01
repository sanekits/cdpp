#!/bin/bash
# make-cdpp_dev_image-bbvpn.sh

die() {
    echo "ERROR: $*" >&2
    exit 1
}


docker pull artifactory.inf.bloomberg.com/dpkg-python-development-base:3.10 || die 101

xhash=$(docker images | grep -E 'artifact.*python.*base.*3\.10' | awk '{print $3}')
[[ -n $xhash ]] || die 102

docker tag $xhash cdpp_dev_image || die 103


