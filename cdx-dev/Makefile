# Makefile for cdx-dev
SHELL=/bin/bash
.ONESHELL:
.SUFFIXES:
MAKEFLAGS += --no-builtin-rules

absdir := $(dir $(realpath $(lastword $(MAKEFILE_LIST))))


ContainerId = $(shell docker ps -a | awk '/cdx-dev/ {print $$1}')

config:
	@set -ue
	cat <<-EOF
	ContainerId=$(ContainerId)
	EOF

dk.up:
	@set -ue
	[[ -n "$(ContainerId)" ]] && {
		docker start "$(ContainerId)"
	} || {
		docker run -d -v `pwd`:/workspace --name cdx-dev -it artprod.dev.bloomberg.com/dpkg-python-development-base:3.11 sleep infinity
	}

dk.stop:
	@set -ue
	docker stop "$(ContainerId)"

dk.shell:
	@set -ue
	docker exec -w /workspace -it "$(ContainerId)" bash

dk.rm:
	@set -ue
	[[ -n "$(ContainerId)" ]] && docker rm -f $(ContainerId) || echo "No container to kill"

env.setup: /.dockerenv
	@set -ue
	ln -sf /workspace/user.bashrc ~/.bashrc
	apt-get install -y tree bash-completion


