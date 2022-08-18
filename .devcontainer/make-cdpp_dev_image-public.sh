#!/bin/bash

die() {
    echo "ERROR: $*" >&2
    exit 1
}

docker pull mcr.microsoft.com/vscode/devcontainers/python:0-3.10 || die
docker tag mcr.microsoft.com/vscode/devcontainers/python:0-3.10 noregistry.localhost/cdpp_dev_image:latest || die
