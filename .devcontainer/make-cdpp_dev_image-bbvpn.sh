#!/bin/bash
# make-cdpp_dev_image-bbvpn.sh

die() {
    echo "ERROR: $*" >&2
    exit 1
}

bbvpnDockerfile() {
    cat <<-EOF
FROM artifactory.inf.bloomberg.com/dpkg-python-development-base:3.10

ENV http_proxy=http://proxy.bloomberg.com:81 \
    https_proxy=http://proxy.bloomberg.com:81 \
    no_proxy=.bloomberg.com,10.0.0.0/8,100.0.0.0/8 \
    NODE_EXTRA_CA_CERTS=/etc/pki/ca-trust/source/anchors/bloomberg_rootca_v2.crt

EOF
}

bbvpnDockerfile  > bbvpn.dockerfile.tmp

docker build -f bbvpn.dockerfile.tmp . || die 101

rm bbvpn.dockerfile.tmp

xhash=$(docker images | grep -E 'artifact.*python.*base.*3\.10' | awk '{print $3}')
[[ -n $xhash ]] || die 102

docker tag $xhash cdpp_dev_image || die 103


