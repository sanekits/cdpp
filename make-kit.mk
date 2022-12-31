# make-kit.mk for <Kitname>
#  This makefile is included by the root shellkit Makefile
#  It defines values that are kit-specific.
#  You should edit it and keep it source-controlled.

# TODO: update kit_depends to include anything which
#   might require the kit version to change as seen
#   by the user -- i.e. the files that get installed,
#   or anything which generates those files.
kit_depends := \
    bin/cdpp.bashrc \
	bin/cdpprc \
	bin/setutils.py \
	bin/termios_proxy.py \
	bin/tox_core.py \
	bin/tox-completion.bash \


publish-common: conformity-check

publish: pre-publish publish-common release-upload release-list
	cat tmp/draft-url
	@echo ">>>> publish complete OK. (FINAL)  <<<"

